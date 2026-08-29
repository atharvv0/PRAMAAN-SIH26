import type { UserRole, AuthUser } from "@/store";

const ACCOUNTS_KEY = "pramaan-local-accounts-v2";

const encoder = new TextEncoder();

export interface LocalAccount {
  id: string;
  name: string;
  email: string;
  org: string;
  role: UserRole;
  salt: string;
  passwordHash: string;
  createdAt: string;
}

function bytesToBase64(bytes: Uint8Array): string {
  let binary = "";

  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }

  return btoa(binary);
}

function base64ToBytes(value: string): Uint8Array {
  const binary = atob(value);

  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

function loadAccounts(): LocalAccount[] {
  try {
    const raw = localStorage.getItem(ACCOUNTS_KEY);

    if (!raw) {
      return [];
    }

    const parsed: unknown = JSON.parse(raw);

    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter((item): item is LocalAccount => {
      if (!item || typeof item !== "object") {
        return false;
      }

      const value = item as Record<string, unknown>;

      return [
        "id",
        "name",
        "email",
        "org",
        "role",
        "salt",
        "passwordHash",
        "createdAt",
      ].every((key) => typeof value[key] === "string");
    });
  } catch {
    return [];
  }
}

function saveAccounts(accounts: LocalAccount[]): void {
  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(accounts));
}

function createSalt(): Uint8Array {
  const webCrypto = globalThis.crypto;

  if (!webCrypto?.getRandomValues) {
    throw new Error(
      "This browser does not provide secure random number generation. Local authentication is unavailable.",
    );
  }

  return webCrypto.getRandomValues(new Uint8Array(16));
}

/**
 * Creates a true ArrayBuffer from the supplied bytes.
 *
 * TypeScript 6's DOM typings distinguish ArrayBuffer from
 * ArrayBufferLike, so passing the original Uint8Array directly
 * can produce a BufferSource type error.
 */
function toArrayBuffer(bytes: Uint8Array): ArrayBuffer {
  const buffer = new ArrayBuffer(bytes.byteLength);

  new Uint8Array(buffer).set(bytes);

  return buffer;
}

async function hashPassword(
  password: string,
  salt: Uint8Array,
): Promise<string> {
  const webCrypto = globalThis.crypto;

  if (!webCrypto?.subtle) {
    throw new Error(
      "This browser does not provide Web Crypto. Secure local authentication is unavailable.",
    );
  }

  const key = await webCrypto.subtle.importKey(
    "raw",
    encoder.encode(password),
    "PBKDF2",
    false,
    ["deriveBits"],
  );

  const bits = await webCrypto.subtle.deriveBits(
    {
      name: "PBKDF2",
      salt: toArrayBuffer(salt),
      iterations: 210_000,
      hash: "SHA-256",
    },
    key,
    256,
  );

  return bytesToBase64(new Uint8Array(bits));
}

function validatePassword(password: string): string | null {
  if (password.length < 12) {
    return "Password must be at least 12 characters.";
  }

  if (!/[A-Z]/.test(password)) {
    return "Password must contain an uppercase letter.";
  }

  if (!/[a-z]/.test(password)) {
    return "Password must contain a lowercase letter.";
  }

  if (!/[0-9]/.test(password)) {
    return "Password must contain a number.";
  }

  if (!/[^A-Za-z0-9]/.test(password)) {
    return "Password must contain a special character.";
  }

  return null;
}

export async function registerLocalAccount(input: {
  id: string;
  name: string;
  email: string;
  org: string;
  password: string;
}): Promise<AuthUser> {
  const id = input.id.trim().toLowerCase();
  const email = input.email.trim().toLowerCase();
  const name = input.name.trim();
  const org = input.org.trim();

  if (!/^[a-z0-9][a-z0-9._-]{2,31}$/.test(id)) {
    throw new Error(
      "User ID must be 3–32 characters and use letters, numbers, dot, underscore, or hyphen.",
    );
  }

  if (!/^\S+@\S+\.\S+$/.test(email)) {
    throw new Error("Enter a valid work email address.");
  }

  if (name.length < 2) {
    throw new Error("Enter your full name.");
  }

  if (org.length < 2) {
    throw new Error("Enter your organization or operating unit.");
  }

  const passwordError = validatePassword(input.password);

  if (passwordError) {
    throw new Error(passwordError);
  }

  const accounts = loadAccounts();

  if (accounts.some((account) => account.id === id)) {
    throw new Error("That user ID is already registered.");
  }

  if (accounts.some((account) => account.email === email)) {
    throw new Error("That email address is already registered.");
  }

  const salt = createSalt();
  const passwordHash = await hashPassword(input.password, salt);

  const account: LocalAccount = {
    id,
    name,
    email,
    org,
    role: "operator",
    salt: bytesToBase64(salt),
    passwordHash,
    createdAt: new Date().toISOString(),
  };

  saveAccounts([...accounts, account]);

  return toAuthUser(account);
}

export async function authenticateLocalAccount(
  identifier: string,
  password: string,
): Promise<AuthUser> {
  const value = identifier.trim().toLowerCase();

  if (!value || !password) {
    throw new Error("Enter your user ID or email and password.");
  }

  const account = loadAccounts().find(
    (item) => item.id === value || item.email === value,
  );

  if (!account) {
    throw new Error("Invalid user ID/email or password.");
  }

  let salt: Uint8Array;

  try {
    salt = base64ToBytes(account.salt);
  } catch {
    throw new Error(
      "This local account record is invalid. Create a new local account.",
    );
  }

  if (salt.byteLength === 0) {
    throw new Error(
      "This local account record is invalid. Create a new local account.",
    );
  }

  const hash = await hashPassword(password, salt);

  if (hash !== account.passwordHash) {
    throw new Error("Invalid user ID/email or password.");
  }

  return toAuthUser(account);
}

export function hasLocalAccounts(): boolean {
  return loadAccounts().length > 0;
}

function toAuthUser(account: LocalAccount): AuthUser {
  return {
    id: account.id,
    name: account.name,
    email: account.email,
    org: account.org,
    role: account.role,
  };
}

export function passwordPolicy(): string {
  return "12+ characters · uppercase · lowercase · number · special character";
}
