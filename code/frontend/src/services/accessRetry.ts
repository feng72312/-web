import { promptAccessCode } from "../components/AccessCodeGate";
import { AccessCodeRequiredError } from "./deviceHeaders";

export async function withAccessCodeRetry<T>(run: () => Promise<T>): Promise<T> {
  let hadStoredCode = Boolean(window.localStorage.getItem("zy_access_code"));
  while (true) {
    try {
      return await run();
    } catch (err) {
      if (!(err instanceof AccessCodeRequiredError)) {
        throw err;
      }
      const code = await promptAccessCode({ invalid: hadStoredCode });
      if (!code) {
        throw new Error("需要访问口令");
      }
      hadStoredCode = true;
    }
  }
}
