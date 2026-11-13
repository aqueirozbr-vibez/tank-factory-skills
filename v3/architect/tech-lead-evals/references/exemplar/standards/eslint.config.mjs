// Standards for fieldco/reading-web, cited by context/code-standards.md.
import tseslint from 'typescript-eslint';

export default tseslint.config(...tseslint.configs.strict, {
  rules: {
    'max-depth': ['error', 3],
    'max-lines-per-function': ['error', { max: 60, skipBlankLines: true, skipComments: true }],
    'no-empty': ['error', { allowEmptyCatch: false }],
    '@typescript-eslint/no-magic-numbers': ['error', { ignore: [0, 1], ignoreEnums: true }],
    '@typescript-eslint/no-floating-promises': 'error',
  },
});
