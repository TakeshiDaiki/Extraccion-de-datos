# Proyecto Ingestly (ex "Master Data Explorer Pro") — Notas

**Nombre para retomar: "Ingestly"** (o "el SaaS de extracción de datos" para que retome el contexto). Renombrado desde "Master Data Explorer Pro" el 2026-07-22 — todas las menciones viejas en este archivo son historial, no hace falta reescribirlas.

- Repo: https://github.com/TakeshiDaiki/Extraccion-de-datos (público)
- Carpeta local: `C:\Users\joses\Documents\Extraccion-de-datos`
- App en vivo: https://master-data-explorer-pro.streamlit.app/
- Entorno virtual local ya creado en `.venv/` con todas las dependencias instaladas

## Qué es el proyecto

Era el proyecto más viejo sin terminar del usuario en GitHub: una plataforma BI en Python con 6 motores ETL simulados (Web Scraping, API, Login Scraping, Email, PDF, Excel), dashboard en Streamlit, y un asistente de IA. Se pivotó a un SaaS demo con registro/login y planes Free/Premium.

## Todo lo hecho hoy (2026-07-19/20), en orden

### 1. Bugs corregidos (proyecto original, antes del pivote a SaaS)
- API Extraction crasheaba (faltaba `api_endpoint`) — `assistant/command_router.py`
- `STRIP_ACCENTS` crasheaba (`.encode()` mal usado en Serie de pandas) — `transform/cleaner.py`
- Motor de email crasheaba (parámetros que no existían) — `core/pipeline.py`
- `UnicodeEncodeError` por emojis en consola Windows no-UTF8 — `core/pipeline.py` (fix de raíz, no solo en el entrypoint)
- `api/main.py` convertido en API FastAPI real con `POST /run-etl` (antes no era una API de verdad, y `jobs/scheduler.py` le pegaba a un endpoint que no existía)
- `load/database.py` apuntaba a una tercera base de datos huérfana — corregido para usar la compartida
- `assistant/chat_interface.py` eliminado (código muerto/duplicado)
- Sistema de "reglas de automatización" (`core/pipeline_manager.py`) que existía pero no tenía UI — se le agregó una pestaña "Automatización" real en el dashboard
- `.gitignore` no cubría `.venv/` (solo `venv/`) — corregido, junto con otras carpetas de runtime

### 2. Pivote a SaaS (a pedido del usuario — quería registro/login y planes tipo suscripción)
Decisiones acordadas explícitamente con el usuario:
- **Pagos: maqueta, no Stripe real todavía** (decisión explícita, revisar si cambia)
- **Stack: se queda en Streamlit** (no se migró a un stack web separado)

Se construyó:
- `auth/` — registro y login con contraseñas hasheadas (bcrypt), tabla `users` en la misma DB compartida
- Planes Free ($0, Web/API/Email, máx 50 registros) vs Premium ($19/mes mock, las 6 fuentes, máx 10.000 registros, reglas de automatización, export a Excel) — gating real aplicado en el dashboard
- Páginas nuevas con `st.navigation`: Landing (Home), Login, Registro (Sign Up), Dashboard (con gating), Planes
- Botón "Actualizar a Premium" es mock: cambia el plan en la DB al instante, sin cobro real

### 3. Deploy a producción
- Repo pasado de privado a público (era necesario para que Streamlit Community Cloud pudiera acceder sin instalar su GitHub App, que dio problemas)
- Deployado en Streamlit Community Cloud: https://master-data-explorer-pro.streamlit.app/
- Bug encontrado y arreglado solo en producción: `ModuleNotFoundError` porque el cwd en Streamlit Cloud es distinto al local — se arregló agregando la raíz del repo a `sys.path` explícitamente en `dashboards/streamlit_app.py`
- **Importante**: la base de datos SQLite es efímera en el plan gratuito de Streamlit Cloud — usuarios registrados se pierden si el contenedor se reinicia. No hay persistencia real todavía.

### 4. Segunda ronda de feedback (hoy mismo, después del primer deploy)
El usuario pidió 5 cosas. Se hicieron 3, se pospusieron 2:
- ✅ **Diseño más profesional**: tema oscuro/indigo consistente vía `.streamlit/config.toml` + módulo de estilo compartido `dashboards/views/_style.py` (headers, cards, tabs con la misma identidad visual en todas las páginas)
- ✅ **Todo el sitio traducido a inglés** (landing, login, registro, dashboard, planes, mensajes de auth) — decisión del usuario: el idioma de un SaaS debe ser inglés (universal)
- ✅ **Landing page con más descripción**: secciones nuevas "How it works" (3 pasos), grid de features, "Who it's for"
- ⏳ **Pagos reales (Stripe)** — el usuario quiere llevarlo a producción pronto, pero se pospuso explícitamente para mañana. Requiere que el usuario cree su propia cuenta de Stripe (Claude no puede crear cuentas ni ingresar credenciales de pago).
- ⏳ **"Olvidé mi contraseña"** — se pospuso para mañana. Requiere servicio de envío de email real (Gmail app password o SendGrid) que el usuario tiene que configurar con sus propias credenciales. La alternativa discutida (no implementada aún) es un flujo demo que muestra el link/código de reset en pantalla en vez de mandarlo por mail.

La página de Planes ya tiene un texto que explica cómo funcionaría el cobro en producción (Stripe, tarjetas aceptadas, a dónde va la plata) aunque hoy sigue siendo 100% maqueta — responde a la pregunta que hizo el usuario hoy.

## Para retomar mañana — pendientes explícitos

1. ~~Conectar Stripe real~~ → **descartado**: Stripe no soporta cuentas registradas en Colombia (la única vía sería formar una empresa real en EEUU vía Stripe Atlas, ~$500 + obligaciones fiscales recurrentes — desproporcionado para un demo). Se pivotó a **PayPal Subscriptions**, código ya implementado (2026-07-20), ver sección abajo. Falta que el usuario cree su cuenta de PayPal y complete `secrets.toml`.
2. **Flujo de "olvidé mi contraseña"** — definir si es demo (código en pantalla) o con email real (requiere que el usuario configure SMTP/SendGrid).
3. Nada más quedó pendiente de la lista de hoy — el resto (diseño, inglés, landing) está terminado y deployado.

## Billing real (2026-07-20) — código listo con PayPal, falta cuenta del usuario

**Historia**: se arrancó implementando Stripe (ver commits de la sesión), pero al momento de crear la cuenta el usuario descubrió que Colombia no aparece en el selector de país de Stripe — no está soportado. Se evaluó Global66 (no sirve, es una cuenta multi-moneda para transferencias puntuales, no tiene cobro recurrente/suscripciones) y pasarelas regionales (Wompi, MercadoPago, PayU — sí soportan Colombia) pero el usuario quería algo de reconocimiento más global. Se confirmó que **PayPal sí opera con cuenta empresarial completa desde Colombia** (retiros vía Davivienda/Nequi) y tiene Subscriptions API con sandbox — se migró todo el código de Stripe a PayPal manteniendo la misma arquitectura.

Implementado (no commiteado todavía):
- `billing/paypal_service.py`: crea una `Subscription` de PayPal (pending approval), verifica el estado server-side al volver (`verify_subscription`, chequea `status == "ACTIVE"` + que el email coincida), cancela la suscripción real al hacer downgrade (`cancel_subscription`). Usa OAuth2 `client_credentials` para autenticar contra la API REST de PayPal (token efímero por request, vía `requests`, sin SDK adicional). Lee credenciales de `st.secrets["paypal"]` (local: `.streamlit/secrets.toml`, prod: Secrets de Streamlit Cloud) con fallback a env vars `PAYPAL_*`.
- El `return_url` que le pasamos a PayPal incluye un marcador propio `?paypal_return=1` — decisión deliberada porque no hay certeza documentada de que PayPal apendee `subscription_id`/`token` al volver, así que controlamos el trigger de verificación nosotros mismos en vez de depender de eso. El subscription_id real se guarda en `st.session_state` al crear la suscripción (antes del redirect) y se usa al volver.
- `auth/db.py` + `auth/service.py`: columna `paypal_subscription_id` en `users` (con migración `ALTER TABLE` si la tabla ya existía); `set_plan()` guarda/limpia el subscription_id; `get_subscription_id()`.
- `dashboards/views/plans.py`: si PayPal está configurado, el botón "Upgrade" abre el flujo real de aprobación de PayPal (login con cuenta sandbox de test); si no está configurado, cae al mock anterior (flip de flag) para no romper el demo. "Switch back to Free" cancela la suscripción real en PayPal antes de bajar el plan — importante, si no seguiría cobrando aunque el usuario "downgradee" en la app.
- `dashboards/streamlit_app.py`: la página Plans tiene `url_path="plans"` fijo (necesario para que el `return_url`/`cancel_url` apunten a una ruta estable).
- `scripts/setup_paypal_plan.py`: script standalone que crea el producto + plan ($19/mes recurring) vía API con `PAYPAL_CLIENT_ID`/`PAYPAL_CLIENT_SECRET` como env vars (el usuario lo corre él mismo, las credenciales nunca pasan por el chat).
- `.streamlit/secrets.toml.example`: template con `client_id`, `client_secret`, `plan_id`, `mode` (sandbox/live), `app_base_url`. `.streamlit/secrets.toml` real está en `.gitignore`.
- `requirements.txt`: sin dependencias nuevas — usa `requests`, que ya era una dependencia del proyecto (paquete `stripe` que se había agregado antes fue removido al pivotar).
- Probado: compile-check de todos los archivos tocados, roundtrip completo de `register_user`/`set_plan`/`get_subscription_id` contra la DB de dev (usuario de prueba borrado después), servidor local levantado sin errores. En navegador se alcanzó a verificar visualmente landing page, registro de cuenta, y que el guard de login bloquea `/plans` sin sesión — la extensión de Chrome se rompió a mitad de sesión (error persistente "Cannot access a chrome-extension:// URL of different extension") antes de poder probar el flujo completo de upgrade/checkout. No se pudo probar con credenciales reales de PayPal (el usuario todavía no tiene cuenta).

**Deliberadamente NO implementado**: webhook de PayPal. La verificación es solo al volver del flujo de aprobación (marcador `paypal_return=1` en la URL + `GET /v1/billing/subscriptions/{id}`), suficiente para el flujo feliz porque Streamlit Community Cloud no puede hostear un endpoint de webhook aparte fácilmente. Limitación conocida: cancelaciones hechas directamente desde la cuenta de PayPal del usuario (fuera de la app) o fallos de cobro en la renovación mensual no se van a reflejar automáticamente en la DB. Si en algún momento se quiere resolver esto, la API FastAPI que ya existe (`api/main.py`) sería un buen lugar para un endpoint `/paypal-webhook`, pero requeriría deployarla en otro servicio (Render/Railway/etc.), no en Streamlit Cloud.

**Estado 2026-07-20 (sesión de tarde/noche)**: el usuario ya convirtió su cuenta de PayPal a Business (eligió "no tiene sitio web", opción válida, se puede agregar después) y creó una app en developer.paypal.com llamada "Master Data Explorer Pro". `.streamlit/secrets.toml` ya existe localmente con `mode = "sandbox"`, pero **el Client ID/Secret que copió son de la app en modo Live** (el toggle del dashboard estaba en "Live", no en "Sandbox"), así que `scripts/setup_paypal_plan.py` falla con `401 invalid_client` al pedir el token OAuth2 — las credenciales Live no funcionan contra el endpoint `api-m.sandbox.paypal.com`.

**Nota de seguridad de la sesión**: en un momento el usuario pegó el Client ID/Secret reales directamente en el chat (y por error los había guardado en `secrets.toml.example`, que si se sube a git). Se corrigió de inmediato: los valores reales se movieron a `.streamlit/secrets.toml` (gitignored) y `secrets.toml.example` volvió a tener placeholders. Se confirmó con `git status`/`git log` que nada llegó a commitearse ni pushearse. Como son credenciales de sandbox (o en este caso Live pero sin ninguna operación real todavía), no se rotaron — pero vale la pena recordarle al usuario en el futuro que edite `secrets.toml` directo (nunca `secrets.toml.example`) y que no pegue credenciales en el chat.

**Para retomar**: 
1. En developer.paypal.com, cambiar el toggle arriba a **Sandbox** (no Live).
2. Ahí buscar/crear la app "Master Data Explorer Pro" en modo sandbox (es una app distinta a la Live, con su propio Client ID/Secret — no son los mismos).
3. Copiar esas credenciales *sandbox* a `.streamlit/secrets.toml` (reemplazando las Live que hay ahora), manteniendo `mode = "sandbox"`.
4. Volver a correr `scripts/setup_paypal_plan.py` para generar el `plan_id`.
5. Completar `secrets.toml`, probar localmente con una cuenta sandbox de comprador (developer.paypal.com/dashboard/accounts — PayPal genera una por defecto).
6. Ahí seguimos con el resto: cargar secrets en Streamlit Cloud, commit + push.

## Sesión 2026-07-20 (noche) — checkout end-to-end probado y funcionando, con 3 bugs reales encontrados y arreglados

Se completó por fin la prueba end-to-end del checkout real de PayPal en el navegador (Chrome volvió a conectar). Se encontraron y arreglaron **tres bugs reales**, ninguno relacionado con las credenciales:

1. **`scripts/setup_paypal_plan.py` pegaba a un endpoint que no existe** (`/v1/catalog/products`, singular) — el endpoint real de PayPal es `/v1/catalogs/products` (plural). Daba 404 con body vacío. Verificado directo contra la API real antes de tocar el código. Ya corregido — el script generó el producto y el `plan_id` real sin problema después del fix.

2. **Bug de arquitectura real en el checkout**: `plans.py` exigía login (`require_login()`) *antes* de procesar el retorno de PayPal (`paypal_return=1`). El problema de fondo: el login de esta app vive solo en `st.session_state` (memoria, sin cookie/token), y **cualquier navegación completa fuera del dominio —como ir a aprobar en PayPal y volver— destruye esa sesión**, sea en la misma pestaña o en una nueva (no es un tema de `st.link_button` abriendo pestaña nueva, es inherente a cualquier ida-y-vuelta a un dominio externo). Resultado: el pago se aprobaba en PayPal pero la app nunca lo registraba, el usuario volvía sin sesión y el plan se quedaba en Free para siempre.
   **Fix**: el email del usuario ahora viaja en el propio `return_url` que le mandamos a PayPal al crear la suscripción (dato que nosotros controlamos, PayPal no lo puede alterar). Al volver, se verifica y graba el Premium en la base usando ese email sin necesitar sesión viva, y se le pide al usuario loguearse de nuevo para *ver* su plan actualizado (deliberadamente no se lo autologuea, para no abrir una puerta de bypass de contraseña). Archivos tocados: `billing/paypal_service.py` (agrega `&email=...` al `return_url`) y `dashboards/views/plans.py` (reordena el guard, lee el email de la URL).
   **Nota de seguridad de la solución**: no hay auto-login server-side tras el pago — el usuario siempre tiene que loguearse con su contraseña para ver el nuevo plan, así que este fix no abre ninguna vía de bypass de autenticación.
   **Pendiente real, no resuelto todavía**: la sesión de la app en general no sobrevive un refresh (F5) porque no hay cookie/token persistente — es una limitación general de esta app de auth-solo-en-memoria, expuesta por este bug pero no arreglada de fondo (sería una feature más grande, tipo "remember me").

3. **`verify_subscription()` no capturaba errores HTTP de PayPal** — un `subscription_id` inválido o un fallo de red tiraba un traceback feo al usuario en vez de un mensaje de error. Ya envuelto en try/except.

**Lección de debugging para el futuro** (costó mucho tiempo esta sesión): en este entorno, el servidor de Streamlit local a veces sigue corriendo con **bytecode cacheado viejo** (`__pycache__/*.pyc`) aunque el archivo `.py` se edite y el proceso se reinicie — y además, matar el proceso con `pkill -f "streamlit run"` desde Git Bash **no mata el proceso real de Windows**, así que "reiniciar" terminaba apilando 2-3 procesos python.exe distintos escuchando todos en el puerto 8501, y el navegador quedaba conectado al más viejo (con código desactualizado) sin ningún error visible. Si un cambio de código "no hace efecto" pese a reiniciar: chequear `netstat -ano | grep :8501` por procesos duplicados y matarlos con `taskkill //F //PID <pid>` (no `pkill`), y borrar `__pycache__` a mano antes de relanzar.

**Probado end-to-end y confirmado funcionando**: registro → login → Upgrade to Premium → aprobación real en PayPal sandbox (cuenta comprador `sb-47asxl52138198@personal.example.com`) → vuelta a la app → "Payment confirmed" → login → **"Current plan: Premium"** reflejado correctamente en la base de datos.

**No commiteado todavía** — falta que el usuario decida cuándo commitear y pushear estos fixes (billing real de PayPal + los 3 bugs corregidos) a `main`.

## Cosas técnicas a tener en cuenta al retomar

- **Hay cambios sin commitear** (billing PayPal completo + fixes de esta sesión) — revisar `git status` antes de asumir que está todo pusheado, a diferencia de sesiones anteriores.
- El deploy en Streamlit Cloud se actualiza solo con cada push a `main` (auto-redeploy).
- Recordar probar SIEMPRE localmente antes de pushear — ya hubo un bug que solo apareció en producción (imports con `sys.path`), así que conviene levantar el server local (`streamlit run dashboards/streamlit_app.py` desde la raíz del repo) antes de cada push grande.
- La base de datos (`database.db`) está en `.gitignore`, no se sube — cada entorno (local, producción) tiene la suya, desconectadas entre sí.
- Si el server local no refleja cambios de código: ver la nota de debugging de arriba (procesos duplicados + bytecode cacheado).
