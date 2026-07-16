import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  User, HeartPulse, FolderHeart, CalendarDays, FlaskConical, Pill,
  ShieldCheck, Watch, IdCard, Users, Settings, LogOut,
} from "lucide-react";
import Dropdown, { DropdownItem, DropdownDivider } from "../ui/Dropdown";
import Avatar from "../ui/Avatar";
import authService from "../../services/authService";

const ITEMS = [
  { label: "My Profile", icon: User, to: "/profile" },
  { label: "Health Profile", icon: HeartPulse, to: "/profile" },
  { label: "Medical Records", icon: FolderHeart, to: "/records" },
  { label: "Appointments", icon: CalendarDays, to: "/appointments" },
  { label: "Reports", icon: FlaskConical, to: "/reports" },
  { label: "Pharmacy Orders", icon: Pill, to: "/pharmacy" },
  { label: "Insurance", icon: ShieldCheck, to: "/insurance" },
  { label: "Connected Devices", icon: Watch, to: "/profile" },
  { label: "ABHA", icon: IdCard, to: "/profile" },
  { label: "Family Members", icon: Users, to: "/profile" },
  { label: "Settings", icon: Settings, to: "/profile" },
];

export default function ProfileDropdown() {
  const navigate = useNavigate();
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user") || sessionStorage.getItem("user") || "null"));
  useEffect(() => { authService.me().then(setUser).catch(() => setUser(null)); }, []);
  const signOut = () => { authService.clearSession(); navigate("/login"); };

  return (
    <Dropdown
      width="w-[264px]"
      trigger={
        <button className="rounded-full outline-none transition-transform hover:scale-[1.04]">
          <Avatar name={user?.name || "Patient"} size={38} />
        </button>
      }
    >
      <div className="mb-1 flex items-center gap-3 px-3 py-3">
        <Avatar name={user?.name || "Patient"} size={40} />
        <div className="min-w-0">
          <p className="truncate text-[14px] font-semibold text-fg">{user?.name || "Patient"}</p>
          <p className="truncate text-[12px] text-fg-muted">{user?.email || user?.phone || ""}</p>
        </div>
      </div>
      <DropdownDivider />

      <div className="no-scrollbar max-h-[320px] overflow-y-auto">
        {ITEMS.map((item) => (
          <DropdownItem key={item.label} icon={item.icon} onClick={() => navigate(item.to)}>
            {item.label}
          </DropdownItem>
        ))}
      </div>

      <DropdownDivider />
      <DropdownItem icon={LogOut} tone="danger" onClick={signOut}>
        Log out
      </DropdownItem>
    </Dropdown>
  );
}
