import Image from "next/image";
import { redirect } from "next/navigation";
export default function Home() {
  // Langsung melempar pengguna ke halaman GoRide Operations
  redirect("/goride");
}