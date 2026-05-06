# Словарь текстовых сообщений
LEXICON_MESSAGES = {
    "welcome": "Добро пожаловать в ФотосессИИ!\n\nПерейдите на канал для выбора стиля, либо же перейдите в \"Творческий режим\" 👇.",
    "profile": "Профиль: {first_name}\n\nДоступно кредитов: {credits}\n\nВыберите действие 👇",
    "history": "<b>История генераций</b>\n\nID: {history_id}\nСтатус: {status}",
    "orders": "Ваши покупки:",
    
    # Подписка
    "sub_required": "Для использования стилей необходимо подписаться на канал — @FotosessII_Pro",
    "sub_bonus": "🎁 Вам начислено 2 кредита за подписку на канал!",
    "sub_not_found": "Вы не подписались на канал!",
    
    # Модерация и публикация
    "pub_offer": "Разрешите опубликовать Вашу фотографию в наш канал как пример для использования данного стиля другими людьми?",
    "pub_sent": "Спасибо! Фото отправлено администратору на проверку. ✨",
    "pub_admin_req": "🔔 <b>Заявка на публикацию</b>\n\n👤 {first_name}{username_str} [<code>{user_id}</code>]\n\n📝 <b>Промпт:</b>\n<blockquote expandable><code>{safe_prompt}</code></blockquote>",
    "pub_req_sent": "Запрос отправлен...",
    "pub_err_gen": "Ошибка при генерации текста.",
    "pub_text_not_changed": "Текст не изменился.",
    "pub_success": "✅ Опубликовано!",
    "pub_rejected": "\n\n❌ <b>Отклонено модератором</b>",
    "pub_final": "❗️ Пользователь <b>{first_name}</b> опубликовал свой результат! 😍\n\n{ai_text}\n\nЧтобы примерить стиль на себе, жми на кнопку 👇\n\n💬 <a href=\"https://t.me/+huj-lW23s0U2MTRi\">Канал</a> | <a href=\"https://t.me/FotosessII_robot\">Бот</a> 🤖",

    # Творческий режим (генерация)
    "creative_prompt_req": "📝 Отправьте мне подробное описание (промпт) того, что вы хотите сгенерировать.",
    "creative_photo_req": "📸 Отлично! Теперь отправьте фото (с лицом), которое хотите использовать как основу.",
    "creative_photo_err": "Пожалуйста, отправьте именно фото (сжатое изображение).",
    "creative_confirm": "Все верно?\n\n<blockquote expandable><code>{prompt}</code></blockquote>",
    "creative_cancel": "Действие отменено.",
    "creative_gen_start": "✅ Подтверждено. Ожидайте...",
    "creative_magic": "🎨 Магия в процессе... {elapsed} сек",
    "creative_delay": "⏳ Процесс затянулся, подождите или попробуйте ещё раз.\nВ случае если результат так и не пришёл — напишите администратору.",
    "creative_err_timeout": "❌ Не удалось получить ответ от сервера генерации. Попробуйте ещё раз.\n🎁 1 кредит автоматически возвращён на ваш баланс.",
    "creative_ready": "✅ Готово! Как вам результат?",
    "creative_no_credits": "Баланс пуст. Пополните баланс.",
    "creative_user_not_found": "Пользователь не найден.",
    "creative_err_api": "❌ Ошибка: API вернул пустую ссылку.\n🎁 1 кредит автоматически возвращён на ваш баланс.",
    "creative_err_status": "⚠️ Ошибка генерации. Статус: {status}\n🎁 1 кредит автоматически возвращён на ваш баланс.",
    "creative_err_no_prompt": "Сначала отправьте текстовый промпт.",
    "creative_err_data": "Ошибка данных. Попробуйте снова.",
    "creative_refund_req": "📦 <b>Запрос на возврат</b>\n\n👤 {first_name}{username_str} [<code>{user_id}</code>]\n\n📝 <b>Промпт:</b>\n<blockquote expandable><code>{safe_prompt}</code></blockquote>",
    "creative_refund_orig": "📷 Оригинал",
    "creative_refund_sent": "Запрос отправлен",
    "creative_refund_admin_btn": "⬆️ Возврат от {first_name} [<code>{user_id}</code>]",
    
    # Стили
    "style_author": "👤 <b>Автор стиля:</b> {author_name}\n🔥 <b>Стиль применили:</b> {count_use} раз\n\nЧтобы получить такой же результат, просто <b>отправьте свое фото</b> следующим сообщением! 👇",
    
    # Ошибки доступа
    "err_foreign_history": "Вы не можете просматривать чужую историю!",
    "err_foreign_profile": "Вы не можете просматривать чужой профиль!",
    "err_foreign_order": "Это не ваш заказ!",
    
    # Покупки и возвраты
    "order_no_history": "У вас еще нет истории покупок 🛒",
    "order_not_found": "Заказ не найден.",
    "order_detail": "<b>Информация о платеже</b>\n\n🆔 ID заказа: <code>{order_id}</code>\n💰 Сумма: {spent} ⭐\n🎯 Кредитов: {credits}\n📋 Статус: {status}\n🕐 Дата: {timestamp}\n",
    "order_detail_tx": "🔑 ID транзакции: <code>{tx_id}</code>\n",
    "order_refund_already": "Этот заказ уже был возвращён.",
    "order_refund_not_paid": "Возврат возможен только для оплаченных заказов.",
    "order_refund_prompt": "✏️ Напишите причину возврата одним сообщением:",
    "order_refund_sent": "📨 Ваш запрос на возврат отправлен администратору. Ожидайте решения.",
    "order_refund_admin_req": "💸 <b>Запрос на возврат средств</b>\n\n👤 {first_name}{username_str} [<code>{user_id}</code>]\n\n🆔 Заказ: <code>{order_id}</code>\n💰 Сумма: {spent} ⭐ → {credits} кредитов\n🔑 ID транзакции: <code>{tx_id}</code>\n🕐 Дата: {timestamp}\n\n📝 <b>Комментарий:</b>\n<blockquote expandable>{comment}</blockquote>",
    "order_refund_err_tx": "Ошибка: ID транзакции отсутствует. Возврат невозможен для этого заказа.",
    
    # Платежи
    "pay_pending_exist": "У вас уже есть незавершённая оплата. Завершите её или попробуйте снова позже.",
    "pay_choose_amount": "Выберите сумму пополнения. 10 ⭐ = 1 кредит, минимальное пополнение 50 ⭐.",
    "pay_unknown_tier": "Неизвестный тариф.",
    "pay_min_amount": "Минимальное пополнение {min_stars} ⭐.",
    "pay_invoice_title": "Пополнение баланса",
    "pay_invoice_desc": "Пополнение на {stars} ⭐ — {credits} кредитов.",
    "pay_err_form": "❌ Не удалось открыть платёжную форму.\nОписание ошибки со стороны платёжной системы:\n{error_text}\n\nℹ️ Убедитесь, что в @BotFather подключены платежи Telegram Stars.",
    "pay_err_create": "❌ Ошибка создания платежа: {error_text}",
    "pay_err_invalid": "Невалидный или устаревший платёж.",
    "pay_already_processed": "Платёж уже обработан или не найден.",
    "pay_success": "✅ Пополнение успешно! Вам зачислено {credits} кредитов.",
    
    # Возвраты со стороны админа
    "adm_refund_success": "🎁 Вам возвращен 1 кредит за неудачную генерацию.",
    "adm_refund_approved": "\n\n✅ Возвращено",
    "adm_refund_rejected": "\n\n❌ Отказано",
}

# Словарь текстов кнопок
LEXICON_BUTTONS = {
    "btn_main_menu": "🏠 В меню",
    "btn_cancel_to_menu": "❌ В меню",
    "btn_cancel": "❌ Отмена",
    "btn_confirm": "✅ Подтвердить",
    "btn_yes_all_good": "✅ Да, все верно",
    "btn_yes": "Да",
    "btn_no": "Нет",
    "btn_topup": "💳 Пополнить баланс",
    "btn_topup_balance": "💎 Пополнить баланс",
    "btn_creative": "🎨 Творческий режим",
    "btn_profile": "👤 Профиль",
    "btn_purchases": "🛍 Мои покупки",
    "btn_history": "📖 История генераций",
    "btn_sub": "Подписаться на канал",
    "btn_sub_check": "✅ Проверить подписку",
    
    "btn_rate_good": "🔥 Отлично",
    "btn_rate_bad": "💩 Ужасно",
    
    "btn_pub_yes": "🚀 Опубликовать",
    "btn_pub_no": "🗑 Отклонить",
    "btn_pub_gen": "🎨 Генерировать",
    "btn_pub_apply": "Применить стиль 🚀",
    
    "btn_refund_credit": "💸 Вернуть кредит",
    "btn_req_refund": "💸 Запросить возврат",
    "btn_nav_prev": "⬅️ Назад",
    "btn_nav_next": "Вперед ➡️",
    "btn_detail": "Детали",
    "btn_refund_funds": "💸 Возврат средств",
    "btn_adm_refund_approve": "✅ Одобрить возврат",
    "btn_adm_refund_reject": "❌ Отказать",
    "btn_adm_ref_ok": "✅ Вернуть",
    "btn_adm_ref_no": "❌ Отказать",
    
    "btn_back": "Назад",
    "btn_back_to_profile": "Назад в профиль",
    "btn_choose_style": "Выбрать готовый стиль",
    "btn_my_profile": "Мой профиль",
    "btn_creative_mode": "Творческий режим",
    "btn_purchases_history": "История покупок",
    "btn_gen_history": "История генераций",
    "btn_topup_no_emoji": "Пополнить баланс",
    
    # Тарифы пополнения
    "btn_tier_50": "50 ⭐ — 5 кредитов",
    "btn_tier_100": "100 ⭐ — 10 кредитов 🚀",
    "btn_tier_200": "200 ⭐ — 25 кредитов",
    "btn_tier_500": "500 ⭐ — 65 кредитов",
    "btn_tier_1000": "🔥 1000 ⭐ — 150 кредитов 🔥",
}
