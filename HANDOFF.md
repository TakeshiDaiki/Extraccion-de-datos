# Guía de traspaso — Master Data Explorer Pro

Este documento es para quien compre o se haga cargo de este proyecto. Explica qué está terminado, qué es maqueta, qué falta, y los pasos exactos para dejarlo funcionando con **tus propias cuentas y credenciales** (las del vendedor no se transfieren — ver sección "Traspaso de cuentas").

Para arquitectura de código y cómo correr el proyecto localmente, ver [`README.md`](README.md). Este documento se enfoca en el estado del negocio/producto, no en la arquitectura técnica.

## 1. Qué está 100% funcional hoy

- **Pipeline de extracción/transformación/carga** (6 fuentes simuladas, limpieza, reglas de automatización, export CSV/Excel).
- **Cuentas de usuario**: registro, login, contraseñas hasheadas con bcrypt.
- **Planes Free/Premium** con límites reales (no solo cosméticos): fuentes disponibles, tope de registros, automatización.
- **Cobro real de Premium vía PayPal Subscriptions** (`billing/paypal_service.py`): checkout, verificación server-side al volver de PayPal, y cancelación real de la suscripción al hacer downgrade (no solo un flag local). Probado end-to-end en modo **sandbox**.
- **Deploy en vivo**: [master-data-explorer-pro.streamlit.app](https://master-data-explorer-pro.streamlit.app/), auto-redeploy en cada push a `main`.

## 2. Qué está construido pero requiere que TÚ lo actives con tus propias credenciales

### 2.1 PayPal → pasar de sandbox a cobro real
El código ya soporta modo `live`, hoy corre en `sandbox` (dinero ficticio). Para cobrar de verdad:
1. Crea (o usa) tu propia cuenta Business de PayPal.
2. En [developer.paypal.com](https://developer.paypal.com), crea una app en modo **Live** (no reutilices la app sandbox del vendedor original — son credenciales distintas e intransferibles a otra cuenta).
3. Corré `scripts/setup_paypal_plan.py` con esas credenciales Live para generar tu propio `plan_id` de $19/mes (o el precio que definas).
4. Completá `[paypal]` en `.streamlit/secrets.toml` (local) y en Streamlit Cloud → Settings → Secrets (producción) con `mode = "live"`.

**Importante**: hasta que hagas esto, el botón de upgrade sigue en modo demo (cambia el plan en la base sin cobrar nada real) — es un fallback deliberado del código, no un bug.

### 2.2 Recuperación de contraseña por email (SendGrid) — código listo, sin activar
Ya existe el flujo completo: página "Forgot Password", generación de código de 6 dígitos (hasheado con bcrypt, expira en 15 min, un solo uso), y el servicio de envío (`notifications/sendgrid_service.py`). **No está activo** porque requiere tu propia cuenta de SendGrid:
1. Crear cuenta en [sendgrid.com](https://sendgrid.com) (capa gratis: 100 emails/día).
2. Verificar un sender (Settings → Sender Authentication → Single Sender Verification) con tu email y dirección física — SendGrid lo exige como requisito anti-spam.
3. Generar una API key con permiso restringido a **Mail Send** únicamente.
4. Completar `[sendgrid]` en `secrets.toml` (local y prod) con `api_key` y `from_email`.

Mientras esto no esté configurado, la página de "Forgot Password" se lo indica al usuario con un mensaje claro en vez de romperse.

## 3. Limitaciones técnicas conocidas (documentadas, no bugs ocultos)

| Limitación | Impacto | Cómo resolverla si hace falta |
|---|---|---|
| Base de datos SQLite efímera en Streamlit Community Cloud free tier | Usuarios y datos se pierden si el contenedor se reinicia | Migrar a Postgres (ej. Supabase/Neon free tier) — cambiar `SQLITE_URL` en `config.py` por una URL de conexión real, SQLAlchemy ya lo soporta sin más cambios |
| Sesión de login solo en `st.session_state` (memoria) | Un F5 (refresh) desloguea al usuario; no hay "remember me" | Agregar un token/cookie persistente (ej. `streamlit-cookies-manager` o JWT propio) |
| No hay webhook de PayPal | Cancelaciones hechas *fuera* de la app (directo en la cuenta de PayPal del usuario) o fallos de cobro en la renovación mensual no se reflejan solos en la base | La API FastAPI (`api/main.py`) ya existe y sería el lugar natural para un endpoint `/paypal-webhook`, pero necesita deployarse aparte (Render/Railway/etc.), Streamlit Cloud no lo soporta directamente |
| Motores de extracción usan datos simulados | No hacen scraping/llamadas reales todavía | Están armados como base — conectar fuentes reales es la extensión más obvia del producto |

## 4. Traspaso de cuentas y credenciales

**No se transfieren cuentas de terceros junto con el código.** Cada credencial en `secrets.toml`/Streamlit Cloud Secrets pertenece a una cuenta personal del vendedor (PayPal, y en el futuro SendGrid) y no debe usarse después de la venta:

- **GitHub**: transferir la propiedad del repo (`Settings → Danger Zone → Transfer ownership`) o dar acceso de colaborador, según lo acordado.
- **Streamlit Community Cloud**: el nuevo dueño debe conectar su propia cuenta y redeployar desde su fork/repo transferido — Streamlit Cloud no transfiere apps entre cuentas.
- **PayPal**: el comprador crea su propia app (sandbox y luego live) — ver sección 2.1. Las credenciales actuales quedan invalidadas/rotadas por el vendedor tras la venta.
- **SendGrid**: igual, cuenta propia del comprador — ver sección 2.2.
- Una vez completada la venta, el vendedor debería rotar (regenerar) cualquier API key que haya existido en `secrets.toml`, aunque nunca haya sido commiteada al repo, como buena práctica.

## 5. Roadmap sugerido para el comprador

En orden de impacto/esfuerzo:
1. Activar PayPal en modo live (2.1) — es lo único que falta para monetizar de verdad.
2. Activar SendGrid (2.2) — cierra un flujo de UX básico que hoy está a medio camino.
3. Migrar a una base de datos persistente (sección 3) — crítico antes de tener usuarios reales, ya que hoy se pueden perder cuentas sin aviso.
4. "Remember me" / sesión persistente — mejora de UX, no bloqueante.
5. Conectar los motores de extracción a fuentes reales — es el corazón del producto y la mayor oportunidad de diferenciación.
6. Webhook de PayPal — importante en cuanto haya usuarios pagando de verdad, para no depender solo de la verificación al vuelo.
