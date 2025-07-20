// Type definitions for debug module
declare module './debug' {
  const debug: {
    init: () => void;
    log: (...args: any[]) => void;
    warn: (...args: any[]) => void;
    error: (...args: any[]) => void;
  };
  
  export default debug;
}
