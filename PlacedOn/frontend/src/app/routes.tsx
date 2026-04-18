import { createBrowserRouter } from "react-router";
import { InterviewRoom } from "./components/InterviewRoom";
import { PreInterviewScreen } from "./components/PreInterviewScreen";
import { DashboardLayout } from "./components/DashboardLayout";
import { UserDashboard } from "./components/UserDashboard";
import { ApplicationsScreen } from "./components/ApplicationsScreen";
import { ProfileScreen } from "./components/ProfileScreen";
import { SettingsScreen } from "./components/SettingsScreen";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: DashboardLayout,
    children: [
      {
        index: true,
        Component: UserDashboard,
      },
      {
        path: "applications",
        Component: ApplicationsScreen,
      },
      {
        path: "profile",
        Component: ProfileScreen,
      },
      {
        path: "settings",
        Component: SettingsScreen,
      },
    ],
  },
  {
    path: "/pre-interview",
    Component: PreInterviewScreen,
  },
  {
    path: "/interview",
    Component: InterviewRoom,
  },
]);
