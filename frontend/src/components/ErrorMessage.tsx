export function ErrorMessage({ message }: { message: string | null }) {
  return message ? <div role="alert" className="error-message">{message}</div> : null;
}
