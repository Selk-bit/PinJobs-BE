# Constants for XPaths and other values
ANCHORS_XPATH = "//a[contains(@href, '/jobs/view')]"
MODAL_DISMISS_XPATH = "//button[contains(@data-tracking-control-name, 'public_jobs_contextual-sign-in-modal_modal_dismiss')]"
TITLE_XPATH = "//h2[contains(@class, 'top-card-layout__title')]"
DESCRIPTION_XPATH = "//div[contains(@class, 'description__text')]"
SALARY_XPATH = "//div[contains(@class, 'compensation__salary')]"
COMPANY_XPATH = "//a[contains(@class, 'topcard__org-name-link')]"
POST_DATE_XPATH = ".//time"
LOCATION_XPATH = "//span[contains(@class, 'topcard__flavor topcard__flavor--bullet')]"
SIGN_IN_BUTTON_XPATH = "//a[contains(@class, 'sign-in-form__sign-in-cta')]"
SUBMIT_BUTTON_XPATH = "//input[contains(@class, 'join-form__form-body-submit-button')]"
USERNAME_INPUT_XPATH = "//input[@id='email-or-phone']"
JOB_RESULTS_XPATH = "//meta[@content='d_jobs_guest_search']"
POPULAR_WEBSITES = [
    "https://www.google.com",
    "https://www.wikipedia.org",
    "https://www.youtube.com",
    "https://www.amazon.com",
    "https://www.facebook.com",
    "https://www.twitter.com",
    "https://www.instagram.com",
    "https://www.reddit.com",
    "https://www.bbc.com",
]
BATCH_SIZE = 5

DEFAULT_TEMPLATE_DATA = {
    'language': 'fr',
    'company_logo': {
        'url': '',
        'border': False,
        'hidden': True,
        'grayscale': False,
        'size': 90,
        'aspectRatio': 1,
        'borderRadius': 50,
    },
    'page': {
        'margin': 12,
        'format': 'a4',
        'headline': True,
        'summary': True,
        'breakLine': False,
        'pageNumbers': False,
    },
    'certifications': {'name': 'Certifications', 'visible': True},
    'education': {'name': 'Education', 'visible': True},
    'experience': {'name': 'Experience', 'visible': True},
    'volunteering': {'name': 'Volunteering', 'visible': True},
    'interests': {'name': 'Interests', 'visible': True},
    'languages': {'name': 'Languages', 'visible': True},
    'projects': {'name': 'Projects', 'visible': True},
    'references': {'name': 'References', 'visible': True},
    'skills': {'name': 'Skills', 'visible': True},
    'social': {'name': 'Social Profiles', 'visible': True},
    'theme': {
        'background': '#fff',
        'text': '#2C3E50',
        'primary': '#16A085',
    },
    'personnel': {
        'name': True,
        'phone': True,
        'city': True,
        'age': True,
        'email': True,
    },
    'typography': {
        'family': 'open-sans',
        'size': 16,
        'lineHeight': 2,
        'hideIcons': False,
        'underlineLinks': False,
    },
}
FRONTEND_PREVIEW_URL = "https://pinjobs-fe.onrender.com/resume-preview/"
FRONTEND_BASE_URL = "https://pinjobs-fe.onrender.com"

WELCOME_QUESTION = {
    "question_type": "welcome",
    "name": "Welcome",
    "text": "Welcome to Career AI Coach!",
    "description": "Navigate your career with AI-powered guidance. Identify opportunities and milestones to shape your professional journey.",
}

SELECT_RESUME_QUESTION = {
    "question_type": "select-resume",
    "name": "Select Resume",
    "text": "Select a Resume",
    "description": "We will use your resume to learn about you and suggest personalized career paths.",
    "choice": 0,
}

FINISH_QUESTION = {
    "question_type": "finish",
    "name": "Career AI Coach Ready",
    "text": "Your Career AI Coach is Ready!",
    "description": "You can change the resume your AI coach is based on as well as your customization via preferences.",
}
