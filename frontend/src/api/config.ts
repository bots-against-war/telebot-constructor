function urlJoin(...args: string[]): string {
  return args.map((pathPart) => pathPart.replace(/(^\/|\/$)/g, "")).join("/");
}

let API_ORIGIN: string;

try {
  // used for local development to serve static files from Vite dev server
  // and point it to the actual locally running Python API server
  // @ts-ignore
  API_ORIGIN = __buildTimeReplacedApiOrigin;
} catch {
  API_ORIGIN = window.location.origin;
}

// replaced at build time by Vite along with HTML/CSS import URLs
// see https://vitejs.dev/guide/build.html#public-base-path
// used when packaging constructor to deploy at subpath within a larger web app
const CONSTRUCTOR_BASE_PATH = import.meta.env.BASE_URL;

const CONSTRUCTOR_BASE_URL = new URL(CONSTRUCTOR_BASE_PATH, API_ORIGIN).href;
const API_BASE_URL = urlJoin(CONSTRUCTOR_BASE_URL, "/api");

console.debug(`API origin: ${API_ORIGIN}`);
console.debug(`Base constructor path: ${CONSTRUCTOR_BASE_PATH}`);
console.debug(`Base API URL: ${API_BASE_URL}`);

export const apiUrl = (route: string) => urlJoin(API_BASE_URL, route);
