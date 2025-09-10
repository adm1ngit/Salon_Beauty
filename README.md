# Salon Booking API (FastAPI)

Bu loyiha **salonlar uchun bron qilish ilovasi** (backend qismi) bo‘lib, FastAPI asosida qurilgan. Unda foydalanuvchilar telefon raqami orqali ro‘yxatdan o‘tishlari, salonlarni qidirishlari, xizmatlarga bron qilishlari, to‘lovlarni amalga oshirishlari va chat orqali ustalar bilan muloqot qilishlari mumkin.

---

## 🚀 Xususiyatlar

* **Ro‘yxatdan o‘tish / Avtorizatsiya** — Telefon raqami va OTP orqali.
* **Profil** — Ism, tug‘ilgan sana, jins, shahar va qiziqishlarni saqlash.
* **Salonlar** — Yaqin atrofdagi salonlarni ko‘rish (geolokatsiya asosida).
* **Qidiruv** — Xizmatlar va salonlarni qidirish.
* **Bron qilish** — Xizmat, vaqt va ustani tanlab, onlayn bron qilish.
* **To‘lovlar** — Payme / Click / Uzum Pay integratsiyasi.
* **Chat** — Foydalanuvchi ↔️ Usta (WebSocket va REST fallback).
* **Push-bildirishnomalar** — FCM orqali eslatmalar va promo xabarlar.
* **Premium obuna** — Cashback ballari va maxsus takliflar.
* **Influencer blog & Promo** — Kontent va maxfiy chegirmalar.

---

## 📂 Papka tuzilmasi

```
salon_app/
├─ alembic/                  # Migratsiyalar
├─ app/
│  ├─ main.py                # Kirish nuqtasi
│  ├─ core/                  # Config, xavfsizlik, utils
│  ├─ db/                    # Session, init_db
│  ├─ models/                # SQLAlchemy modellari
│  ├─ schemas/               # Pydantic modellari
│  ├─ api/v1/                # Routers
│  ├─ services/              # OTP, Payment, Notification
│  ├─ core_tasks/            # Background jobs
│  └─ tests/                 # Testlar
├─ migrations/               # Alembic
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ README.md
```

---

## ⚙️ O‘rnatish

### 1. Repo klonlash

```bash
git clone https://github.com/ZiyodilloYigitaliyev/Salon-Booking.git
cd Salon-Booking
```

### 2. Virtual environment yaratish

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Kutubxonalarni o‘rnatish

```bash
pip install -r requirements.txt
```

### 4. `.env` fayl yaratish

Misol:

```
DATABASE_URL=postgresql://user:pass@localhost:5432/salon_db
SECRET_KEY=changeme
SMS_PROVIDER_API_KEY=xxx
FCM_SERVER_KEY=xxx
PAYME_MERCHANT_ID=xxx
PAYME_SECRET=xxx
```

### 5. Migratsiyalarni ishga tushirish

```bash
alembic upgrade head
```

### 6. Serverni ishga tushirish

```bash
uvicorn app.main:app --reload
```

---

## 📡 API Endpoints (qisqacha)

* `POST /api/v1/auth/request-otp` — OTP yuborish
* `POST /api/v1/auth/verify-otp` — OTP tasdiqlash va token olish
* `GET /api/v1/salons/nearby` — Yaqin atrofdagi salonlar
* `POST /api/v1/bookings/` — Bron qilish
* `POST /api/v1/payments/create` — To‘lov yaratish
* `GET /api/v1/chat/{salon_id}/ws` — WebSocket orqali chat

---

## 🧪 Testlar

```bash
pytest -v
```

---

## 📌 Reja (bosqichma-bosqich)

1. **MVP**: Auth (OTP), User profil, Salon listing, Booking (basic), Chat (REST).
2. **Keyingi**: To‘lov integratsiyasi, Push notifications, Review system.
3. **Premium**: Obuna, Cashback, Blog, Promo.
4. **Scaling**: Redis caching, PostGIS, Load balancing.

---

## 🤝 Hissa qo‘shish

Pull requestlar ochiq. Har qanday tavsiya va xatolik haqida issue qoldiring.

---

## 📄 Litsenziya

MIT License — erkin foydalanish mumkin.
