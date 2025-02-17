from django.contrib import admin
from .models import (Candidate, CV, CVData, Job, JobSearch, Payment, CreditPurchase, Template, Keyword, Location,
                     ScrapingSetting, Pack, Price, CreditAction, KeywordLocationCombination, Favorite, AbstractTemplate,
                     Ad, GeneralSetting, SearchTerm, UserProfile, Language, Question, AnswerSet,
                     AnswerOption, CandidateResponse, Career, CareerTranslation, CandidateCareer)
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from datetime import datetime
import logging
from import_export import widgets
from django import forms
from django.core.exceptions import ValidationError



logger = logging.getLogger(__name__)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified']


@admin.register(AbstractTemplate)
class AbstractTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'reference', 'image', 'created_at', 'updated_at']
    search_fields = ['name', 'reference']
    list_filter = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'language', 'abstract_template', 'get_cv', 'created_at', 'updated_at'
    ]
    search_fields = ['abstract_template__name', 'abstract_template__reference', 'language']
    list_filter = ['language', 'created_at', 'updated_at']
    autocomplete_fields = ['abstract_template']
    ordering = ['abstract_template__name', 'language']

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    fieldsets = (
        (None, {
            'fields': ('abstract_template', 'language')
        }),
        ('Details', {
            'fields': (
                'company_logo', 'page', 'certifications', 'education', 'experience',
                'volunteering', 'interests', 'languages', 'projects', 'references',
                'skills', 'social', 'theme', 'personnel', 'typography'
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def get_cv(self, obj):
        """Display the associated CV ID."""
        if hasattr(obj, 'cv'):
            return obj.cv.id  # Display the CV ID or any field you prefer
        return "No CV"

    get_cv.short_description = "CV ID"


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'get_username', 'get_email', 'phone', 'credits')
    search_fields = ('first_name', 'last_name', 'user__username', 'user__email')

    # Access the username through the related User model
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    # Access the email through the related User model
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    readonly_fields = ("generated_pdf", "thumbnail")
    list_display = ('id', 'candidate', 'cv_type', 'created_at', 'updated_at')
    search_fields = ('candidate__first_name', 'candidate__last_name')

    def delete_model(self, request, obj):
        if obj.template:
            obj.template.delete()
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # Iterate through the queryset to delete associated templates
        for cv in queryset:
            if cv.template:
                cv.template.delete()  # Delete the associated template
        super().delete_queryset(request, queryset)


@admin.register(CVData)
class CVDataAdmin(admin.ModelAdmin):
    list_display = ['cv', 'title', 'name', 'email', 'phone', 'updated_at']
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = ('cv__candidate__first_name', 'cv__candidate__last_name')


class NullableIntegerWidget(widgets.IntegerWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value == '':
            return None
        return super().clean(value, row=row, *args, **kwargs)


class JobResource(resources.ModelResource):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements', 'company_name', 'company_logo',
            'company_size', 'location', 'linkedin_profiles', 'employment_type',
            'original_url', 'salary_range', 'min_salary', 'max_salary',
            'benefits', 'skills_required', 'posted_date', 'expiration_date',
            'industry', 'job_type', 'job_id'
        ]
        export_order = fields
        skip_unknown = True
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ("job_id",)

    def before_import_row(self, row, **kwargs):
        """
        Clean data before importing:
        - Convert empty strings to None for specific fields.
        - Convert 'posted_date' to a datetime object.
        - Handle row skipping logic for duplicates and outdated jobs.
        """
        # Fields that should convert empty strings to None
        nullable_fields = ['company_size', 'min_salary', 'max_salary']

        for field in nullable_fields:
            if row.get(field) == '':
                row[field] = None

        # Handle 'posted_date' - convert empty strings to None or parse valid date
        if 'posted_date' in row:
            if row['posted_date'] == '':
                row['posted_date'] = None
            else:
                try:
                    row['posted_date'] = datetime.strptime(row['posted_date'], "%Y-%m-%d").date()
                except ValueError:
                    logger.warning("Invalid date format for posted_date: %s", row['posted_date'])
                    row['posted_date'] = None

        # Handle 'expiration_date' - convert empty strings to None or parse valid date
        if 'expiration_date' in row:
            if row['expiration_date'] == '':
                row['expiration_date'] = None
            else:
                try:
                    row['expiration_date'] = datetime.strptime(row['expiration_date'], "%Y-%m-%d").date()
                except ValueError:
                    logger.warning("Invalid date format for expiration_date: %s", row['expiration_date'])
                    row['expiration_date'] = None

        # Handle missing job_id
        job_id = row.get('job_id')
        if not job_id:
            logger.warning("Skipping row with missing job_id: %s", row)
            return None

        # Skip duplicate job_id
        if Job.objects.filter(job_id=job_id).exists():
            logger.info("Skipping duplicate job_id: %s", job_id)
            return None

        # Check for duplicate jobs with (title, company_name, location)
        existing_job = Job.objects.filter(
            title=row.get('title'),
            company_name=row.get('company_name'),
            location=row.get('location')
        ).first()

        if existing_job:
            csv_posted_date = row.get('posted_date')
            if csv_posted_date and existing_job.posted_date:
                # Compare dates
                if csv_posted_date > existing_job.posted_date:
                    # Update fields for the existing job
                    for field in self.get_fields():
                        if field.attribute in row and field.attribute not in ['id', 'created_at', 'updated_at']:
                            setattr(existing_job, field.attribute, row.get(field.attribute))
                    existing_job.updated_at = datetime.now()
                    existing_job.save()
                    logger.info("Updated existing job: %s", existing_job)
                    return None  # Skip row after updating
                else:
                    logger.info("Skipping row, existing job is newer or equal: %s", existing_job)
                    return None

        return row  # Proceed with creating a new job


@admin.register(Job)
class JobAdmin(ImportExportModelAdmin):
    resource_class = JobResource
    list_display = ('id', 'title', 'company_name', 'location', 'employment_type', 'job_type', 'posted_date')
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = ('title', 'company_name', 'location')

    def has_import_permission(self, request):
        return True


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'original_url', 'is_active')
    search_fields = ('title', 'description', 'original_url')


@admin.register(JobSearch)
class JobSearchAdmin(admin.ModelAdmin):
    list_display = ('job', 'cv', 'similarity_score', 'search_date')
    search_fields = ('cv__name', 'job__title')


@admin.register(CreditPurchase)
class CreditPurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'candidate', 'credits_purchased', 'timestamp')
    search_fields = ('candidate__first_name',)


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword']
    fields = ['keyword']
    search_fields = ['keyword__keyword']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['location']
    fields = ['location']
    search_fields = ['location__location']


@admin.register(GeneralSetting)
class GeneralSettingAdmin(admin.ModelAdmin):
    list_display = ['ads_per_page', 'max_recent_search_terms', 'last_updated']
    list_editable = ['ads_per_page', 'max_recent_search_terms']
    list_display_links = None
    help_texts = {"ads_per_page": "Set the number of ads displayed on each page."}


@admin.register(ScrapingSetting)
class ScrapingSettingAdmin(admin.ModelAdmin):
    list_display = ('num_jobs_to_scrape', 'is_scraping')


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['pack', 'credits', 'price']
    search_fields = ['pack__name', 'credits']
    list_filter = ['pack']


@admin.register(CreditAction)
class CreditActionAdmin(admin.ModelAdmin):
    list_display = ['action_name', 'credit_cost']
    search_fields = ['action_name']


@admin.register(KeywordLocationCombination)
class KeywordLocationCombinationAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'location', 'is_scraped']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'created_at']


@admin.register(SearchTerm)
class SearchTermAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'term', 'is_active', 'last_searched_at']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


class QuestionAdminForm(forms.ModelForm):
    existing_identifiers = forms.ChoiceField(
        required=False,
        label="Existing Group Identifier",
        help_text="Select an existing group identifier to auto-fill."
    )

    class Meta:
        model = Question
        fields = '__all__'  # Ensure group_identifier is first

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch unique existing group identifiers
        existing_identifiers = list(Question.objects.values_list('group_identifier', flat=True).distinct())

        # Set choices dynamically
        self.fields['existing_identifiers'].choices = [("", "Select an existing identifier")] + [
            (identifier, identifier) for identifier in existing_identifiers
        ]

        # Ensure the field order is correct
        field_order = list(self.fields.keys())

        # Remove existing_identifiers if already at the bottom
        if "existing_identifiers" in field_order:
            field_order.remove("existing_identifiers")

        # Insert it right after "group_identifier"
        field_order.insert(field_order.index("group_identifier") + 1, "existing_identifiers")
        # Apply the new order
        self.order_fields(field_order)

        # Add randomization buttons (Customizing widget rendering)
        self.fields["group_identifier"].widget.attrs["data-randomize"] = "true"

    def clean(self):
        cleaned_data = super().clean()
        existing_identifier = cleaned_data.get("existing_identifiers")
        group_identifier = cleaned_data.get("group_identifier")
        language = cleaned_data.get("language")
        answer_set = cleaned_data.get("answer_set")  # Get the selected answer set

        # Auto-fill group identifier if selected
        if existing_identifier:
            cleaned_data["group_identifier"] = existing_identifier

        # Exclude current instance when checking for duplicates (avoid validation on update)
        query = Question.objects.filter(group_identifier=cleaned_data["group_identifier"], language=language)
        if self.instance.pk:  # If updating (not creating), exclude the current instance
            query = query.exclude(pk=self.instance.pk)

        # Prevent duplicate question with the same group_identifier and language
        if query.exists():
            raise ValidationError("A question with this Group Identifier and Language already exists.")

        # 🔹 **Validation: Ensure the selected Answer Set has the same language as the Question**
        if answer_set and answer_set.language != language:
            raise ValidationError("The selected Answer Set must have the same language as the Question.")

        return cleaned_data

    class Media:
        js = ("admin/js/question_identifier_randomizer.js",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = [
        "group_identifier",
        "existing_identifiers",
        "language",
        "name",
        "text",
        "description",
        "question_type",
        "required",
        "answer_set",
    ]
    form = QuestionAdminForm
    list_display = ("name", "language", "group_identifier")
    list_filter = ("language", "group_identifier")
    search_fields = ("name", "group_identifier")

    class Media:
        js = ("admin/js/question_admin.js", "admin/js/fill_answer_set_fields.js")


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 3


@admin.register(AnswerSet)
class AnswerSetAdmin(admin.ModelAdmin):
    list_display = ("name", "language")

    def get_changeform_initial_data(self, request):
        """
        This method is called by the admin when rendering the Add/Change form.
        We can look at GET params and use them to populate initial field values.
        """
        initial = super().get_changeform_initial_data(request)

        # Grab our custom query params (if any) that we appended
        prefill_name = request.GET.get("prefill_name")
        prefill_language = request.GET.get("prefill_language")

        # Use them to populate defaults for new AnswerSet
        if prefill_name:
            initial["name"] = prefill_name
        if prefill_language:
            initial["language"] = prefill_language

        return initial

    inlines = [AnswerOptionInline]


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("answer_set", "text")


class CandidateResponseAdminForm(forms.ModelForm):
    class Meta:
        model = CandidateResponse
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initially, clear choices for selected_option and selected_options
        self.fields["selected_option"].queryset = AnswerOption.objects.none()
        self.fields["selected_options"].queryset = AnswerOption.objects.none()

        # If updating an instance, prepopulate valid options
        if self.instance and self.instance.question_id:
            answer_set = self.instance.question.answer_set
            question_type = self.instance.question.question_type if self.instance.question else None

            if answer_set:
                answer_options = AnswerOption.objects.filter(answer_set=answer_set)

                # Dynamically set options based on question type
                if question_type == Question.RADIO:
                    self.fields["selected_option"].queryset = answer_options
                    self.fields["selected_options"].widget.attrs["disabled"] = True
                elif question_type == Question.CHECKBOX:
                    self.fields["selected_options"].queryset = answer_options
                    self.fields["selected_option"].widget.attrs["disabled"] = True

    def clean(self):
        """
        Ensures that only ONE response type is provided per question and that the answer type aligns with the question type.
        """
        cleaned_data = super().clean()
        text_answer = cleaned_data.get("text_answer")
        selected_option = cleaned_data.get("selected_option")
        selected_options = cleaned_data.get("selected_options")

        # Count the number of filled fields
        filled_fields = [field for field in [text_answer, selected_option, selected_options] if field]
        if len(filled_fields) > 1:
            raise ValidationError("Only one response type (text, single choice, multiple choices) can be filled.")

        # Validate based on question type
        question = cleaned_data.get("question")
        if question:
            if question.question_type == Question.RADIO and not selected_option:
                raise ValidationError("For radio-type questions, you must select a single option.")
            if question.question_type == Question.CHECKBOX and not selected_options:
                raise ValidationError("For checkbox-type questions, you must select at least one option.")
            if question.question_type == Question.TEXT and not text_answer:
                raise ValidationError("For text-based questions, a text answer must be provided.")

        return cleaned_data


@admin.register(CandidateResponse)
class CandidateResponseAdmin(admin.ModelAdmin):
    form = CandidateResponseAdminForm
    list_display = ("candidate", "question")

    class Media:
        js = ("admin/js/filter_answer_options.js",)


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("group_identifier",)


@admin.register(CareerTranslation)
class CareerTranslationAdmin(admin.ModelAdmin):
    list_display = ("title", "career", "language")


@admin.register(CandidateCareer)
class CandidateCareerAdmin(admin.ModelAdmin):
    list_display = ("candidate", "career")
