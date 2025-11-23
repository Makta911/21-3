from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user_email, user_name=None):
    """
    Отправка приветственного письма после регистрации
    """
    subject = 'Добро пожаловать в наш интернет-магазин!'

    if user_name:
        greeting = f'Уважаемый(ая) {user_name},'
    else:
        greeting = 'Уважаемый пользователь,'

    message = f"""
    {greeting}

    Благодарим вас за регистрацию в нашем интернет-магазине!

    Теперь вы можете:
    - Просматривать каталог товаров
    - Создавать заказы
    - Отслеживать статус заказов
    - Получать специальные предложения

    Если у вас возникли вопросы, пожалуйста, свяжитесь с нашей службой поддержки.

    С уважением,
    Команда интернет-магазина
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )


def send_password_reset_email(user_email, reset_url):
    """
    Отправка письма для сброса пароля
    """
    subject = 'Восстановление пароля'

    message = f"""
    Уважаемый пользователь,

    Вы запросили восстановление пароля для вашей учетной записи.

    Для установки нового пароля перейдите по ссылке:
    {reset_url}

    Если вы не запрашивали восстановление пароля, проигнорируйте это письмо.

    С уважением,
    Команда интернет-магазина
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )