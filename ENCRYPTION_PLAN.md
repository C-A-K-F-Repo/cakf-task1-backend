# Personal Data Encryption Plan

This project uses application-level encryption for user personal data before storing it in PostgreSQL.

PostgreSQL documents multiple encryption layers: storage/filesystem encryption, SSL transport encryption, column encryption via extensions such as `pgcrypto`, and application-level encryption. For this app, application-level encryption is used because the API can keep decryption keys outside the database while PostgreSQL stores only ciphertext.

## Encrypted Fields

- `users.email`
- `users.full_name`
- `users.phone_number`
- `users.dob`
- `users.delivery_address`

The following fields are not encrypted because they are operational/security metadata:

- `users.id`
- `users.role`
- `users.is_active`
- `users.hashed_password`

## Lookup Fields

Email and phone still need equality lookup and uniqueness checks. The app stores HMAC blind indexes:

- `users.email_lookup`
- `users.phone_number_lookup`

These are generated with `PERSONAL_DATA_LOOKUP_KEY`, which must be different from `PERSONAL_DATA_ENCRYPTION_KEY`.

## Required Environment Variables

Generate two different 32-byte base64 keys:

```bash
openssl rand -base64 32
openssl rand -base64 32
```

Set them in the runtime environment:

```env
PERSONAL_DATA_ENCRYPTION_KEY="..."
PERSONAL_DATA_LOOKUP_KEY="..."
```

Losing `PERSONAL_DATA_ENCRYPTION_KEY` makes encrypted personal data unrecoverable. Rotating either key requires a planned re-encryption migration/job.

## Migration Plan

1. Set both env keys in all backend runtime environments.
2. Deploy code with `app/core/personal_data_crypto.py` and encrypted user model columns.
3. Run Alembic migration `9c1d2e3f4a5b_encrypt_user_personal_data.py`.
4. Verify login, registration, notification recipient resolution, user export, and admin/staff user lists.
5. Back up the keys separately from database backups.

## Residual Risks

- Data is decrypted in app memory for legitimate API responses and notifications.
- Redis still temporarily stores pending email/phone update values.
- Existing old database backups may contain plaintext values.
- JWT/localStorage can still expose claims if sensitive fields are added to tokens; avoid adding PII to JWT payloads.
