import type { FC } from "react";
import LogoMaintenancePage from "./branded";
import DefaultMaintenancePage from "./default";
import IllustrationMaintenancePage from "./illustration";
import BlockSection from "../../../components/block-section";
import BlockPageBreadcrumb from "../../../components/block-breadcrumb";

const AllMaintenancePages: FC = function () {
  return (
    <>
      <BlockPageBreadcrumb
        title="Maintenance Pages"
        description="Get started with maintenance pages coded with Tailwind CSS to show your users when you are currently working on an update and the website is not accessible."
      />
      <BlockSection
        title="Default maintenance page"
        description="Use this example to let your users know that you are working on an important update and the website is down for a couple of hours."
        githubLink="https://github.com/themesberg/flowbite-react-blocks/blob/main/pages/marketing-ui/maintenance-pages/default.tsx"
      >
        <DefaultMaintenancePage />
      </BlockSection>
      <BlockSection
        title="Maintenance page with logo"
        description="Use this example to also show your logo alongside the maintenance notice heading and paragraph."
        githubLink="https://github.com/themesberg/flowbite-react-blocks/blob/main/pages/marketing-ui/maintenance-pages/branded.tsx"
      >
        <LogoMaintenancePage />
      </BlockSection>
      <BlockSection
        title="Maintenance page with illustration"
        description="Use this example to also show a visually impactful illustration when notifying your users that your website is being updated."
        githubLink="https://github.com/themesberg/flowbite-react-blocks/blob/main/pages/marketing-ui/maintenance-pages/illustration.tsx"
      >
        <IllustrationMaintenancePage />
      </BlockSection>
    </>
  );
};

export default AllMaintenancePages;
