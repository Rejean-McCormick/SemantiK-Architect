// architect_frontend/src/types/language.ts

export interface Language {
  /**
   * The ISO 639-1 code (e.g., "en", "fr", "zu").
   * This is the strictly enforced public identifier for the API.
   * Public UI language codes are ISO-2 application codes such as "en" and "fr".
   */
  code: string;

  /**
   * The display name of the language (e.g., "English", "Zulu").
   */
  name: string;

  /**
   * The Abstract Wikipedia Z-ID (e.g., "Z1002").
   * Optional linkage to the Wikifunctions ecosystem.
   */
  z_id?: string;
}