/**
 * Root page — redirects to the login page.
 * Developer: Daksh Walia, B.Tech AIML, CGC Mohali
 */

import { redirect } from "next/navigation";

export default function RootPage() {
  redirect("/login");
}
