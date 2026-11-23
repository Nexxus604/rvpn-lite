# R-VPN Lite

Приложение VPN-сервиса R-VPN+: одна кнопка, а сервер и способ подключения для вашей сети приложение выбирает само. Работает по подписке в боте [@rvpnplus_bot](https://t.me/rvpnplus_bot), ничего отдельно покупать не нужно.

**Основной сайт загрузки — [download.plus.rvpn.space/lite](https://download.plus.rvpn.space/lite/).** Здесь резервная копия тех же файлов: каждая новая версия появляется в [Releases](https://github.com/Nexxus604/rvpn-lite/releases/latest) в течение часа после выхода на сайте.

## Скачать

| Система | Файл |
| --- | --- |
| Android | [R-VPN-Lite.apk](https://github.com/Nexxus604/rvpn-lite/releases/latest/download/R-VPN-Lite.apk) |
| Windows 10 и 11 (x64) | [R-VPN-Lite-Windows-x64.exe](https://github.com/Nexxus604/rvpn-lite/releases/latest/download/R-VPN-Lite-Windows-x64.exe) |
| Ubuntu 24.04 и новее (64 бит) | [R-VPN-Lite_amd64.deb](https://github.com/Nexxus604/rvpn-lite/releases/latest/download/R-VPN-Lite_amd64.deb) — `sudo apt install ./R-VPN-Lite_amd64.deb` |
| Fedora 39 и новее, AlmaLinux и Rocky 10 (64 бит) | [R-VPN-Lite.x86_64.rpm](https://github.com/Nexxus604/rvpn-lite/releases/latest/download/R-VPN-Lite.x86_64.rpm) — `sudo dnf install ./R-VPN-Lite.x86_64.rpm` |
| Роутеры с OpenWrt 24.10 и 25.12 | установка одной командой — [ниже](#роутеры) |
| iPhone, iPad и Mac | скоро в App Store; пока подключайтесь через Happ или INCY — ссылки и инструкции в боте |

Если телефон спросит, разрешить ли установку из браузера или Telegram, — разрешите. Если Windows покажет «Неизвестный издатель», нажмите «Подробнее» → «Выполнить в любом случае».

## Как войти

1. Установите и запустите приложение.
2. Введите свой Telegram ID — он на первом экране бота [@rvpnplus_bot](https://t.me/rvpnplus_bot), строка «🆔 Ваш ID». Нажмите на число, чтобы скопировать.
3. Нажмите «Войти» — бот пришлёт 6-значный код. Введите его в приложении.

## Роутеры

Подключитесь к роутеру по SSH (`ssh root@192.168.1.1`) и выполните команду — она сама выберет пакет под процессор роутера:

```sh
wget -qO- https://download.plus.rvpn.space/lite/install-router.sh | sh
```

Если основной сайт не открывается, та же установка с GitHub:

```sh
wget -qO- https://github.com/Nexxus604/rvpn-lite/releases/latest/download/install-router.sh | RVPN_BASE=https://github.com/Nexxus604/rvpn-lite/releases/latest/download sh
```

Затем в настройках роутера откройте «Службы» → «R-VPN Lite» и войдите своим Telegram ID и кодом из бота. Подходят роутеры с OpenWrt 24.10 или 25.12 и флеш-памятью от 32 МБ; роутер займёт одно устройство в подписке.

## Проверка файлов

В каждом выпуске есть `SHA256SUMS` — те же контрольные суммы, что на основном сайте: `sha256sum -c SHA256SUMS --ignore-missing`.

## Поддержка

Бот [@rvpnplus_bot](https://t.me/rvpnplus_bot) или support@rocketvpn.net.

## Лицензия

R-VPN Lite — закрытое программное обеспечение Xenex Networks LLC ([LICENSE.md](LICENSE.md)), исходный код не публикуется. Сторонние компоненты и их лицензии — [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

## English

R-VPN Lite is the app of the R-VPN+ VPN service: one button, and the app picks the server and the protocol that work in your network. It runs on a subscription from the Telegram bot [@rvpnplus_bot](https://t.me/rvpnplus_bot).

The main download site is [download.plus.rvpn.space/lite](https://download.plus.rvpn.space/lite/); this repository keeps a backup copy of the same files in [Releases](https://github.com/Nexxus604/rvpn-lite/releases/latest), updated within an hour of every release. Builds: Android, Windows 10/11 (x64), Ubuntu 24.04+ (.deb), Fedora 39+ / AlmaLinux / Rocky 10 (.rpm) and routers with OpenWrt 24.10 / 25.12; iPhone, iPad and Mac are coming to the App Store. Sign in with your Telegram ID (first screen of the bot, «🆔 Ваш ID») and the 6-digit code the bot sends.
