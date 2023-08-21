// TODO: make configurable with Vite build step
const BASE_PATH = "";

console.debug(`Base path = ${BASE_PATH}`);

// TODO: add configuration for base url to allow serving frontend from dev server
export const apiUrl = (route: string) => BASE_PATH + route;
