import "./globals.css";
import {PwaRegister} from "./pwa-register";

export const metadata = {
  title: "AIRA Academy",
  description: "Multilingual learning with AIRA Tutor",
  manifest: "/manifest.webmanifest",
  icons: { icon: "/icons/aira-academy.svg" },
  appleWebApp: { capable: true, title: "AIRA Academy", statusBarStyle: "default" as const }
};

export const viewport = { themeColor: "#171717", width: "device-width", initialScale: 1 };

export default function RootLayout({children}:{children:React.ReactNode}){
  return <html lang="en"><body><PwaRegister/>{children}</body></html>
}
