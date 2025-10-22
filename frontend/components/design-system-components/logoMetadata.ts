/**
 * Auto-generated logo dimensions
 * Generated on: 2025-02-28T18:50:24.617Z
 */

const logoMetadata = {
  '128': {
    chat: {
      width: 372,
      height: 128,
      alt: 'RAG app',
    },
    'cleanlab-chat': {
      width: 838,
      height: 128,
      alt: 'RAG app',
    },
    'cleanlab-codex': {
      width: 922,
      height: 128,
      alt: 'RAG app',
    },
    'cleanlab-docs': {
      width: 856,
      height: 128,
      alt: 'Cleanlab Docs logo',
    },
    'cleanlab-documentation': {
      width: 1356,
      height: 128,
      alt: 'Cleanlab Documentation logo',
    },
    'cleanlab-studio': {
      width: 924,
      height: 128,
      alt: 'Cleanlab Studio logo',
    },
    'cleanlab-tlm': {
      width: 814,
      height: 128,
      alt: 'Cleanlab TLM logo',
    },
    cleanlab: {
      width: 568,
      height: 128,
      alt: 'Cleanlab logo',
    },
    codex: {
      width: 456,
      height: 128,
      alt: 'RAG app',
    },
    docs: {
      width: 390,
      height: 128,
      alt: 'Cleanlab Docs logo',
    },
    'logo-flush': {
      width: 100,
      height: 128,
      alt: 'Cleanlab logo',
    },
    logo: {
      width: 128,
      height: 128,
      alt: 'Cleanlab logo',
    },
    studio: {
      width: 450,
      height: 128,
      alt: 'Cleanlab Studio logo',
    },
    tlm: {
      width: 356,
      height: 128,
      alt: 'Cleanlab TLM logo',
    },
  },
  '512': {
    chat: {
      width: 1488,
      height: 512,
      alt: 'Cleanlab Chat logo',
    },
    'cleanlab-chat': {
      width: 3354,
      height: 512,
      alt: 'Cleanlab Chat logo',
    },
    'cleanlab-codex': {
      width: 3688,
      height: 512,
      alt: 'Cleanlab Codex logo',
    },
    'cleanlab-docs': {
      width: 3424,
      height: 512,
      alt: 'Cleanlab Docs logo',
    },
    'cleanlab-documentation': {
      width: 5422,
      height: 512,
      alt: 'Cleanlab Documentation logo',
    },
    'cleanlab-studio': {
      width: 3696,
      height: 512,
      alt: 'Cleanlab Studio logo',
    },
    'cleanlab-tlm': {
      width: 3256,
      height: 512,
      alt: 'Cleanlab TLM logo',
    },
    cleanlab: {
      width: 2274,
      height: 512,
      alt: 'Cleanlab logo',
    },
    codex: {
      width: 1822,
      height: 512,
      alt: 'Cleanlab Codex logo',
    },
    docs: {
      width: 1558,
      height: 512,
      alt: 'Cleanlab Docs logo',
    },
    'logo-flush': {
      width: 402,
      height: 512,
      alt: 'Cleanlab logo',
    },
    logo: {
      width: 512,
      height: 512,
      alt: 'Cleanlab logo',
    },
    studio: {
      width: 1800,
      height: 512,
      alt: 'Cleanlab Studio logo',
    },
    tlm: {
      width: 1420,
      height: 512,
      alt: 'Cleanlab TLM logo',
    },
  },
  '1024': {
    chat: {
      width: 2976,
      height: 1024,
      alt: 'Cleanlab Chat logo',
    },
    'cleanlab-chat': {
      width: 6708,
      height: 1024,
      alt: 'Cleanlab Chat logo',
    },
    'cleanlab-codex': {
      width: 7376,
      height: 1024,
      alt: 'Cleanlab Codex logo',
    },
    'cleanlab-docs': {
      width: 6848,
      height: 1024,
      alt: 'Cleanlab Docs logo',
    },
    'cleanlab-documentation': {
      width: 10846,
      height: 1024,
      alt: 'Cleanlab Documentation logo',
    },
    'cleanlab-studio': {
      width: 7392,
      height: 1024,
      alt: 'Cleanlab Studio logo',
    },
    'cleanlab-tlm': {
      width: 6512,
      height: 1024,
      alt: 'Cleanlab TLM logo',
    },
    cleanlab: {
      width: 4550,
      height: 1024,
      alt: 'Cleanlab logo',
    },
    codex: {
      width: 3644,
      height: 1024,
      alt: 'Cleanlab Codex logo',
    },
    docs: {
      width: 3116,
      height: 1024,
      alt: 'Cleanlab Docs logo',
    },
    'logo-flush': {
      width: 804,
      height: 1024,
      alt: 'Cleanlab logo',
    },
    logo: {
      width: 1024,
      height: 1024,
      alt: 'Cleanlab logo',
    },
    studio: {
      width: 3600,
      height: 1024,
      alt: 'Cleanlab Studio logo',
    },
    tlm: {
      width: 2842,
      height: 1024,
      alt: 'Cleanlab TLM logo',
    },
  },
} as const

/**
 * Type for logo height names
 */
type LogoHeight = keyof typeof logoMetadata

/**
 * Type for logo names within a specific height
 */
type LogoName<T extends LogoHeight> = keyof (typeof logoMetadata)[T]

/**
 * Helper function to get logo dimensions with type safety
 */
function getlogoMetadata<T extends LogoHeight>(height: T, logo: LogoName<T>) {
  return logoMetadata[height][logo]
}

export type { LogoHeight, LogoName }
export { getlogoMetadata, logoMetadata }
