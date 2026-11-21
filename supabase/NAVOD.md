# Založení databáze kalendáře v Supabase

Asi 10 minut. Vše je zdarma (tarif Free).

## 1. Účet a projekt
1. Otevřete **https://supabase.com** → **Start your project** → zaregistrujte se
   (ideálně týmovým e-mailem, ať k tomu má přístup i někdo další).
2. **New project**:
   - **Name:** `follow-me`
   - **Database Password:** klikněte na **Generate a password** a uložte si ho
     do správce hesel (nikomu ho neposílejte, ani Claudovi)
   - **Region:** **Central EU (Frankfurt)**
   - **Create new project** → asi 2 minuty počkejte, než se projekt připraví.

## 2. Tabulka a pravidla přístupu
1. Vlevo **SQL Editor** → **New query**.
2. Vložte celý obsah souboru `supabase/schema.sql` → **Run**.
3. Dole musí být **Success** (hlášky „… does not exist, skipping“ jsou v pořádku).

## 3. Vypnout registraci cizích lidí
1. Vlevo **Authentication** → **Sign In / Providers** (případně **Providers**).
2. U **Email** nechte zapnuté, ale **vypněte „Allow new users to sign up“**
   (v části User Signups) → **Save**.

## 4. Účty správců
Pro každého, kdo má kalendář upravovat:
1. **Authentication** → **Users** → **Add user** → **Create new user**
   → e-mail + heslo, zaškrtněte **Auto Confirm User** → **Create user**.
2. V **SQL Editor** spusťte (s jeho e-mailem, malými písmeny):
   ```sql
   insert into public.admins (email) values ('jmeno@example.com') on conflict do nothing;
   ```
Bez druhého kroku se správce přihlásí, ale nic neuloží.

## 5. Co poslat Claudovi
**Project Settings** (ozubené kolo) → **Data API** / **API Keys**:
- **Project URL** – tvar `https://abcdefgh.supabase.co`
- **anon public** klíč (nebo **Publishable key**, začíná `sb_publishable_…`)

Obojí je veřejné a bezpečné poslat do chatu.
**Neposílejte** `service_role` / **Secret key** ani heslo databáze.
