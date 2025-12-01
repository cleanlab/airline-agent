import { FlatCompat } from '@eslint/eslintrc'
import js from '@eslint/js'
import tsParser from '@typescript-eslint/parser'
import tailwindcss from 'eslint-plugin-tailwindcss'
import unusedImports from 'eslint-plugin-unused-imports'
import simpleImportSort from 'eslint-plugin-simple-import-sort'
import { rules as customRules } from '@cleanlab/design-system/lint'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all
})

export default [
  // Ignore generated files
  {
    ignores: [
      '**/*.gen.ts',
      '**/*.gen.tsx',
      'client/**/*.gen.ts',
      'client/**/*.gen.tsx'
    ]
  },
  ...compat.extends(
    'next/core-web-vitals',
    'next/typescript',
    'prettier',
    'plugin:tailwindcss/recommended'
  ),
  {
    plugins: {
      tailwindcss,
      'unused-imports': unusedImports,
      'simple-import-sort': simpleImportSort,
      cleanlab: { rules: customRules }
    },

    languageOptions: {
      globals: {
        React: 'readonly'
      }
    },

    settings: {
      tailwindcss: {
        callees: ['cn', 'cva'],
        config: 'tailwind.config.js'
      }
    },

    rules: {
      'tailwindcss/no-custom-classname': 'off',
      'tailwindcss/classnames-order': 'off',

      'no-restricted-syntax': [
        'error',
        {
          selector:
            'MemberExpression[object.name="React"][property.name=/^use[A-Z]/]',
          message:
            'Import hooks directly from React instead of using React namespace (e.g., use "import { useState } from \'react\'" instead of "React.useState")'
        }
      ],

      'no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'tailwind-variants',
              message: 'Import from `@cleanlab/design-system/utils` instead'
            },
            {
              name: 'tailwind-merge',
              message: 'Import from `@cleanlab/design-system/utils` instead'
            }
          ]
        }
      ],

      'react-hooks/exhaustive-deps': 'error',
      'simple-import-sort/exports': 'error',
      'simple-import-sort/imports': 'error',
      'no-unused-vars': 'off',
      'no-undef': 'error',
      'unused-imports/no-unused-imports': 'error',

      'unused-imports/no-unused-vars': [
        'warn',
        {
          vars: 'all',
          varsIgnorePattern: '^_',
          args: 'after-used',
          argsIgnorePattern: '^_'
        }
      ],

      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          args: 'all',
          argsIgnorePattern: '^_',
          caughtErrors: 'all',
          caughtErrorsIgnorePattern: '^_',
          destructuredArrayIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          ignoreRestSiblings: true
        }
      ],
      'object-shorthand': ['error', 'properties'],
      'no-useless-rename': 'error',
      'no-console': ['error', { allow: ['warn', 'error', 'info'] }],
      'react/jsx-curly-brace-presence': [
        'error',
        { props: 'never', children: 'never' }
      ],
      'cleanlab/cn-no-trivial': 'error'
    }
  },
  {
    files: ['**/*.ts', '**/*.tsx'],

    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: './tsconfig.json',
        tsconfigRootDir: __dirname
      }
    },
    rules: {
      '@typescript-eslint/consistent-type-exports': [
        'error',
        { fixMixedExportsWithInlineTypeSpecifier: true }
      ],
      '@typescript-eslint/consistent-type-imports': [
        'error',
        { fixStyle: 'inline-type-imports' }
      ]
    }
  },
  {
    files: ['**/react-query.gen.ts'],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/ban-ts-comment': 'off'
    }
  },
  {
    files: [
      '**/*.test.ts',
      '**/*.test.tsx',
      '**/*.spec.ts',
      '**/*.spec.tsx',
      '**/tests/**/*',
      '**/__tests__/**/*'
    ],
    rules: {
      '@typescript-eslint/no-explicit-any': 'off'
    }
  }
]
