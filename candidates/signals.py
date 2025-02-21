from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from .models import (Keyword, Location, KeywordLocationCombination, CV, Template, AbstractTemplate, CVData, UserProfile,
                     Candidate, JobSearch)
from django.contrib.auth.models import User
from .constants import DEFAULT_TEMPLATE_DATA
from .utils import (generate_cv_pdf, construct_only_score_job_prompt, construct_candidate_profile,
                    get_gemini_response, construct_similarity_prompt, detect_cv_language)
import json
from datetime import datetime


@receiver(post_save, sender=Keyword)
def create_combinations_for_new_keyword(sender, instance, **kwargs):
    locations = Location.objects.all()
    for location in locations:
        KeywordLocationCombination.objects.get_or_create(keyword=instance, location=location)


@receiver(post_save, sender=Location)
def create_combinations_for_new_location(sender, instance, **kwargs):
    keywords = Keyword.objects.all()
    for keyword in keywords:
        KeywordLocationCombination.objects.get_or_create(keyword=keyword, location=instance)


@receiver(pre_save, sender=CV)
def enforce_single_base_cv(sender, instance, **kwargs):
    if instance.cv_type == CV.BASE:
        CV.objects.filter(candidate=instance.candidate, cv_type=CV.BASE).exclude(id=instance.id).delete()


@receiver(pre_delete, sender=CV)
def delete_template_with_cv(sender, instance, using, **kwargs):
    if instance.template:
        instance.template.delete()


@receiver(post_save, sender=CV)
def create_default_template(sender, instance, created, **kwargs):
    """
    Signal to create a default template for newly created CVs if none exists,
    and only if the abstract template "sydney" is available.
    """
    if created and not instance.name:
        try:
            if instance.cv_type == CV.BASE:
                title = instance.cv_data.title if hasattr(instance, 'cv_data') and instance.cv_data.title else "Untitled"
                instance.name = f"{title} - Base CV"
            elif instance.cv_type == CV.TAILORED:
                if instance.job:
                    job_title = instance.job.title if instance.job.title else "Untitled Job"
                    company_name = instance.job.company_name if instance.job.company_name else "Unknown Company"
                    instance.name = f"{job_title} - {company_name}"
                elif instance.career:
                    base_cv = CV.objects.filter(candidate=instance.candidate, cv_type=CV.BASE).first()
                    if base_cv:
                        base_cv_lang = detect_cv_language(base_cv.cv_data)
                        career_translation = instance.career.translations.filter(language__code=base_cv_lang if base_cv_lang else "en").first()
                        instance.name = f"{career_translation.title} - Tailored CV" if career_translation else "Untitled"
                    else:
                        instance.name = "Untitled - Tailored CV"
                else:
                    instance.name = "Untitled - Tailored CV"
            else:
                instance.name = "Untitled"

            instance.save(update_fields=["name"])
        except Exception as e:
            instance.name = "Untitled"
            instance.save(update_fields=["name"])
            print(f"Error setting CV name: {e}")

    if created and not instance.template:
        try:
            # Retrieve the abstract template "sydney"
            abstract_template = AbstractTemplate.objects.get(name="sydney")
        except AbstractTemplate.DoesNotExist:
            # If "sydney" does not exist, do nothing
            return

        # Create the default template
        template = Template.objects.create(
            abstract_template=abstract_template,
            language=DEFAULT_TEMPLATE_DATA['language'],
            company_logo=DEFAULT_TEMPLATE_DATA['company_logo'],
            page=DEFAULT_TEMPLATE_DATA['page'],
            certifications=DEFAULT_TEMPLATE_DATA['certifications'],
            education=DEFAULT_TEMPLATE_DATA['education'],
            experience=DEFAULT_TEMPLATE_DATA['experience'],
            volunteering=DEFAULT_TEMPLATE_DATA['volunteering'],
            interests=DEFAULT_TEMPLATE_DATA['interests'],
            languages=DEFAULT_TEMPLATE_DATA['languages'],
            projects=DEFAULT_TEMPLATE_DATA['projects'],
            references=DEFAULT_TEMPLATE_DATA['references'],
            skills=DEFAULT_TEMPLATE_DATA['skills'],
            social=DEFAULT_TEMPLATE_DATA['social'],
            theme=DEFAULT_TEMPLATE_DATA['theme'],
            personnel=DEFAULT_TEMPLATE_DATA['personnel'],
            typography=DEFAULT_TEMPLATE_DATA['typography'],
        )

        # Associate the template with the CV
        instance.template = template
        instance.save()


@receiver(post_save, sender=CVData)
def handle_cv_update(sender, instance, **kwargs):
    """
    Signal triggered when CVData or Template is created/updated.
    """
    # Determine the associated CV instance
    if sender == CVData:
        cv = instance.cv
        try:
            if not cv.name or "Untitled" in cv.name:
                if cv.cv_type == CV.BASE:
                    title = instance.headline if instance.headline else "Untitled"
                    if not instance.title:
                        CVData.objects.filter(id=instance.id).update(title=title)
                    cv.name = f"{title} - Base CV"
                    cv.save(update_fields=["name"])

        except Exception as e:
            print(f"Error updating CV name after CVData save: {e}")

    elif sender == Template:
        try:
            cv = CV.objects.get(template=instance)
        except CV.DoesNotExist:
            cv = None

    if cv and cv.cv_data and cv.cv_data.name and cv.template:
        cv_lang = detect_cv_language(instance)
        language_choices = Template._meta.get_field('language').choices
        language_values = [choice[0] for choice in language_choices]
        template_lang = cv_lang if cv_lang in language_values else None
        Template.objects.filter(id=cv.template.id).update(language=template_lang)

        # Generate PDF if both cv_data and template exist
        generate_cv_pdf(cv)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)

        # Set is_verified to True for Google-created users
        if not instance.has_usable_password():
            profile.is_verified = True
            profile.save()


@receiver(post_save, sender=User)
def create_candidate(sender, instance, created, **kwargs):
    if created:
        Candidate.objects.get_or_create(user=instance)


@receiver(pre_save, sender=CVData)
def track_previous_state(sender, instance, **kwargs):
    if instance.pk:
        # Fetch the previous instance
        previous_instance = sender.objects.get(pk=instance.pk)
        instance._previous_instance = previous_instance  # Attach it to the current instance


@receiver(post_save, sender=CVData)
def generate_score_for_tailored_cv(sender, instance, created, **kwargs):
    """
    Signal to generate a similarity score for a tailored CV after the CVData is updated,
    only if the previous `title`, `name`, and `email` fields were None.
    """
    # Skip on creation; only run on update
    if created:
        return

    # Fetch the previous state of the instance
    if hasattr(instance, '_previous_instance'):
        previous_instance = instance._previous_instance

        # Check if the previous values for `title`, `name`, and `email` were None
        if previous_instance.title is not None or previous_instance.name is not None or previous_instance.email is not None:
            return  # Do nothing if any of the fields were not None before the update

        # Ensure this is for a tailored CV and that it's full
        if instance.cv.cv_type != instance.cv.TAILORED and instance.name:
            return

        try:
            # Get the associated job for the tailored CV
            job = instance.cv.job
            if not job:
                return  # No associated job; nothing to score

            candidate = instance.cv.candidate
            base_cv = CV.objects.filter(candidate=candidate, cv_type=CV.BASE).first()

            if not base_cv or not hasattr(base_cv, 'cv_data'):
                return  # Base CV or its data is missing; cannot proceed

            # Construct the prompt for Gemini
            tailored_cv_data = instance
            job_data = {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "requirements": ', '.join(job.requirements or []),
                "skills": ', '.join(job.skills_required or [])
            }
            candidate_profile = construct_candidate_profile(tailored_cv_data)

            prompt = construct_similarity_prompt(candidate_profile, [job_data])

            # Fetch the similarity score from Gemini
            gemini_response = get_gemini_response(prompt)
            gemini_response = (gemini_response.split("```json")[-1]).split("```")[0]

            score_data = json.loads(gemini_response)[0]
            score = score_data.get("score", 0)

            job_search = JobSearch.objects.filter(cv=base_cv, job=job).first()
            if job_search and job_search.similarity_score >= score:
                score = job_search.similarity_score + 5

            # Create or update the JobSearch instance
            JobSearch.objects.update_or_create(
                cv=instance.cv,
                job=job,
                defaults={"similarity_score": score, "last_scored_at": datetime.now()}
            )

        except Exception as e:
            # Log the error for debugging purposes
            print(f"Failed to generate similarity score for tailored CV: {e}")


@receiver(pre_save, sender=JobSearch)
def prevent_small_similarity_score_changes(sender, instance, **kwargs):
    """
    Ensure the similarity_score is only updated if the new score differs
    from the old score by more than -2 or +2.
    """
    if instance.pk:  # Only check for updates, not creation
        try:
            # Get the existing JobSearch instance
            old_instance = JobSearch.objects.get(pk=instance.pk)
            old_score = old_instance.similarity_score
            new_score = instance.similarity_score

            # Check if the new score is within the range of -2 to +2
            if -2 <= new_score - old_score <= 2:
                # If within range, keep the old score
                instance.similarity_score = old_score
        except JobSearch.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            pass
