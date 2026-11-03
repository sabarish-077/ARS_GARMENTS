# Security operations

## Rate limits

Public POST attempts are limited per endpoint and client address. The application stores only an HMAC digest of the address in `store_ratelimitbucket`, not the address itself. Limits are:

- Sign-in: 10 attempts per 15 minutes.
- Registration and order tracking: 5 and 12 attempts per 15 minutes, respectively.
- Contact, B2B enquiries, and newsletter: 5 attempts per hour per endpoint.

Requests over the limit receive HTTP 429 and a `Retry-After` header. Apply migrations after pulling the change. On deployments behind a reverse proxy, configure the proxy to set the trusted client address as `REMOTE_ADDR`; this code intentionally does not trust a caller-supplied `X-Forwarded-For` header. Schedule this command daily to remove inactive identity digests:

```powershell
py manage.py prune_rate_limit_buckets
```

## MySQL accounts

Use separate database accounts: `ars_garments_app` for web requests (data read/write only) and `ars_garments_migrator` for schema migrations. Create them from a MySQL administrative account, replacing each password placeholder with a different strong password. Keep those passwords only in the local `.env` or deployment secret store.

```sql
CREATE USER 'ars_garments_app'@'127.0.0.1' IDENTIFIED BY 'REPLACE_WITH_UNIQUE_APP_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE ON ars_garments.* TO 'ars_garments_app'@'127.0.0.1';

CREATE USER 'ars_garments_migrator'@'127.0.0.1' IDENTIFIED BY 'REPLACE_WITH_DIFFERENT_MIGRATION_PASSWORD';
GRANT ALL PRIVILEGES ON ars_garments.* TO 'ars_garments_migrator'@'127.0.0.1';
```

Set `MYSQL_USER=ars_garments_app` and `MYSQL_PASSWORD` to the app password in `.env`. Add `MYSQL_MIGRATION_USER=ars_garments_migrator` and `MYSQL_MIGRATION_PASSWORD` with the separate migration password. Run migrations with the migrator credentials:

The `MYSQL_MIGRATION_PASSWORD` value must be set in `.env` or the process environment, and must match the password assigned to that MySQL account. If it is missing, Django stops early with a configuration error. Never paste database passwords into chat or commit them to source control.

```powershell
$env:DJANGO_DB_MIGRATION = 'True'
py manage.py migrate
Remove-Item Env:DJANGO_DB_MIGRATION
```

When `DJANGO_DB_MIGRATION` is not enabled, Django uses the limited app account. Production settings reject MySQL `root` and require a database password. For a remote MySQL server, replace the SQL account host `127.0.0.1` with the application server's specific source address; avoid `%` unless network controls require and protect that broader host match.

### Troubleshooting account setup

MySQL accounts are the pair `user` + `host`; an account at `localhost` is distinct from one at `127.0.0.1`. Check which account rows exist and which privileges your Workbench connection has:

```sql
SELECT CURRENT_USER(), USER();
SELECT User, Host FROM mysql.user WHERE User = 'ars_garments_migrator';
```

Use the exact `Host` returned by the second query in `ALTER USER`, `CREATE USER`, `GRANT`, and `SHOW GRANTS`. If there is no row for the intended host, connect in Workbench as a MySQL administrator (for example the local `root` account), run `CREATE USER` first, and then run `GRANT`. `GRANT` does not create the missing account. If there is an existing row for another host, either alter/grant that exact account and ensure Django connects from a matching host, or create a separate account for the intended host.

If `CREATE USER` fails with error 1396, that account/host pair already exists; use `ALTER USER` for that exact pair instead. If an `ALTER USER` or `GRANT` command fails with an access error, reconnect in Workbench using an administrator account with user-management privileges. After changing a password, update the corresponding `MYSQL_PASSWORD` or `MYSQL_MIGRATION_PASSWORD` entry in `.env` to exactly the same new value.

If Django reports MySQL error 1044 for `ars_garments_migrator`, the credentials authenticated but that account lacks privileges on the database. As an administrator, find the account's exact host with the query above, then grant schema privileges to that same account/host pair. Re-run `SHOW GRANTS` to confirm before retrying `migrate`.
