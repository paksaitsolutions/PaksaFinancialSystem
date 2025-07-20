// Type definitions for debug module
declare const debug: {
  init: () => void;
  log: (...args: any[]) => void;
  warn: (...args: any[]) => void;
  error: (...args: any[]) => void;
};

export default debug;

declare global {
  interface Window {
    $debug: {
      init: () => void;
      log: (...args: any[]) => void;
      warn: (...args: any[]) => void;
      error: (...args: any[]) => void;
    };
  }
}
