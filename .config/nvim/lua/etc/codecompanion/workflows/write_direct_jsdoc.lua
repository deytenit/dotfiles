return {
  ["Write Direct JSDoc"] = {
    strategy = "workflow",
    description = "Automatically write JSDoc documentation for the current buffer and validate it",
    opts = {
      index = 10,
      is_default = true,
      short_name = "direct-jsdoc",
    },
    prompts = {
      -- First group: Initial setup and documentation generation
      {
        {
          role = "system", -- Use string directly
          content = [[You are an expert TypeScript/JavaScript developer specializing in writing comprehensive JSDoc documentation. You understand all JSDoc tags and patterns including @module, @kind, @typeParam, @param, @returns, and others. You write clear, concise, and accurate documentation that follows best practices.]],
          opts = {
            visible = false,
          },
        },
        {
          role = "user", -- Use string directly
          content = function(context)
            -- Enable auto tool mode
            vim.g.codecompanion_auto_tool_mode = true
            return string.format(
              [[### Задача: Написание JSDoc-документации

Мне нужно, чтобы ты проанализировал код в текущем буфере и составил для него JSDoc-документацию.

### Требования к документации:

1. **На уровне модуля**: Добавь тег @module в начале файла, если это модульный файл[1]
2. **Классы**: Документируй с описанием, используй @typeParam для дженериков, @param для параметров конструктора
3. **Методы**: Включи описание, @param для каждого параметра, @returns для возвращаемых значений
4. **Свойства**: Добавь описания для полей класса и статических полей
5. **Перечисления (Enums)**: Используй @kind enum для объектов, похожих на перечисления
6. **Типы/Интерфейсы**: Добавь описание типа и описания для каждого его поля
7. **Переменные/Константы**: Добавь описания
8. **Специальные типы**: Используй соответствующие теги @kind:
   - @kind action для Redux-действий
   - @kind apiMethod для API-вызовов
   - @kind component для React-компонентов
   - @kind helper для вспомогательных функций
   - @kind selector для селекторов состояния
   - @kind thunk для асинхронных операций
9. **Generic**: Используй @typeParam {generic type} для каждой переменной типа

### Инструкции:

1. Проанализируй код в #{buffer}{watch}
2. Используй инструмент @{full_stack_dev} для генерации полной JSDoc-документации в соответствии с вышеуказанными требованиями
3. Затем используй инструмент @{cmd_runner} для валидации документации командой: `pnpm exec modules-docgen validate {path_to_module}` [2]

### Общие требования

- Не пиши типы переменных, возвращаемых значений и т.д. в документации, если файл typescript
- Считай modules-docgen validate видом теста, следовательно тебе требуется выставлять флаг `testing`, как сказано ранее

### Аннотации

[1] файл, определяющий модуль по feature-sliced-design: {slice}/{module}/index.ts. Не нужно добавлять, если дан иной файл.
[2] Путь в docgen нужно писать к модулю в котором находится компонент по feature-sliced-design, например: `./src/{slice}/{module}`

Выполните все три действия.]],
              context.bufname,
              context.bufname
            )
          end,
          opts = {
            auto_submit = false,
          },
        },
      },
      -- Second group: Handle validation failures
      {
        {
          role = "user", -- Use string directly
          content = [[The documentation validation failed. Please review the error output above and fix the JSDoc documentation accordingly. Make sure to:

1. Fix any missing or incorrect JSDoc tags
2. Ensure all parameters and return types are documented
3. Add any missing @kind tags
4. Correct any syntax errors in the documentation

Use the @{files} tool to update the buffer with the corrected documentation, then run the validation again with @{cmd_runner}.]],
          opts = {
            auto_submit = true,
          },
          condition = function()
            -- Only run if cmd_runner was used and validation failed
            return _G.codecompanion_current_tool == "cmd_runner"
          end,
          repeat_until = function(chat)
            return chat.tools.flags.testing == true
          end,
        },
      },
      -- Third group: Success confirmation
      {
        {
          role = "user", -- Use string directly
          content = [[Excellent! The JSDoc documentation has been successfully written and validated. The documentation now includes:

- All required JSDoc tags
- Proper parameter and return type documentation
- Appropriate @kind tags for special cases
- Clear and concise descriptions

The file has been updated with the validated documentation.]],
          opts = {
            auto_submit = false,
          },
          condition = function()
            -- Only show when validation succeeds
            local last_cmd_output = vim.g.codecompanion_last_cmd_output or ""
            return last_cmd_output:match("Exit code: 0") ~= nil
          end,
        },
      },
    },
  },
}
