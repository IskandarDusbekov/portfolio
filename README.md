# Portfolio (Django)

Django asosida qurilgan portfolio + blog loyihasi.

Loyiha dizayni saqlangan holda backend to'liq ishlaydigan holatga keltirilgan:
- portfolio kontenti admin orqali boshqariladi
- blog postlar admin orqali boshqariladi
- kontakt formasi DB ga yoziladi
- Django Admin `Jazzmin` bilan chiroyli UI ga o'tkazilgan

## Texnologiyalar

- Python 3.11+
- Django
- django-jazzmin
- SQLite (default)
- Pillow (image upload uchun)

## Arxitektura

### `apps.main`
- `Profile`: sayt egasi haqida asosiy ma'lumotlar
- `Skill`: marquee ichidagi skill lar
- `Project`: featured projectlar
- `SocialLink`: footer social linklar
- `ContactMessage`: kontakt formadan kelgan xabarlar

### `apps.blog`
- `BlogCategory`: blog kategoriya
- `BlogPost`: blog maqola (`views_count` bilan)

## Muhim URL lar

- `/` - Asosiy sahifa
- `/blog/` - Blog sahifa
- `/blog/<slug>/` - Blog detail sahifa
- `/admin/` - Django admin (Jazzmin theme bilan)
- `/contact/` - Kontakt form submit endpoint (POST)

## O'rnatish

### 1. Repository

```bash
git clone <repo-url>
cd portfolio
```

### 2. Virtual environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Dependencies

```bash
pip install -r requirements.txt
```

### 4. Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Superuser

```bash
python manage.py createsuperuser
```

### 6. Ishga tushirish

```bash
python manage.py runserver
```

## Admindan kontent boshqarish tartibi

1. `/admin/` ga kiring.
2. `Profile` da asosiy bio ma'lumotlarni kiriting (`is_active=True`).
3. `Skill` larni `sort_order` bilan tartiblang.
4. `Project` larni kiriting (`tech_stack` ni vergul bilan yozing).
5. `BlogCategory` va `BlogPost` larni kiriting.
6. `BlogPost` uchun:
   - `is_published=True` bo'lsa saytda ko'rinadi
   - Featured post avtomatik ravishda eng so'nggi postlar orasidan random tanlanadi
   - `views_count` admin orqali qo'lda ham o'zgartiriladi
7. `ContactMessage` da foydalanuvchi yuborgan xabarlarni ko'rasiz.

## Blog funksiyalari

- Server-side pagination (`/blog/?page=2`)
- Category filter (`/blog/?category=<slug>`)
- Featured post (latest pool ichidan random)
- Post detail sahifasida avtomatik view counter (+1)
- Related postlar va oldingi/keyingi navigatsiya

## Xavfsizlik yangilanishlari

- `SECRET_KEY` env orqali boshqariladi
- `ALLOWED_HOSTS` env orqali boshqariladi
- `CSRF_TRUSTED_ORIGINS` env orqali boshqariladi
- `SESSION_COOKIE_HTTPONLY=True`
- `CSRF_COOKIE_HTTPONLY=True`
- `SECURE_CONTENT_TYPE_NOSNIFF=True`
- `X_FRAME_OPTIONS=DENY`
- `DEBUG=False` holatda secure cookie, HSTS, HTTPS redirect yoqiladi
- Contact form spamdan himoya:
  - honeypot field
  - IP bo'yicha 30 soniyalik throttling

### Tavsiya etilgan `.env` qiymatlar (production)

```env
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=replace-with-strong-secret
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```

## Dizayn haqida

Frontend dizayn o'zgartirilmagan; mavjud UI saqlangan. Backend ulanishi qo'shilgan:
- oldin hardcoded bo'lgan data endi DB dan olinadi
- kontakt formasi endi real server endpoint ga yuboradi

## Testlar

```bash
python manage.py test
```

## Production tavsiyalar

- `DEBUG=False`
- `SECRET_KEY` ni env orqali boshqaring
- `ALLOWED_HOSTS` ni to'ldiring
- static/media ni alohida servis orqali serving qiling (Nginx/S3 va h.k.)

## GitHub workflow tavsiya

Har bir mantiqiy o'zgarishni alohida commit qiling.

Tavsiya etilgan commit format:
- `feat(main): add profile/project/contact models and views`
- `feat(blog): add category/post models and dynamic blog rendering`
- `chore(admin): integrate jazzmin and improve admin panels`
- `docs(readme): add setup, architecture and deployment guide`

PR yozishda quyidagilarni kiriting:
- Nima o'zgardi
- Nima uchun o'zgardi
- Qanday test qilindi
- Ekran rasmlari (agar UI ta'sir qilsa)

## Eslatma

Agar eski `venv` boshqa Python manziliga bog'langan bo'lsa, yangi `venv` yaratib oling.
