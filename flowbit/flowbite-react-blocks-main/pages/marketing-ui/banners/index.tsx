import type { FC } from "react";
import BlockSection from "../../../components/block-section";
import BlockPageBreadcrumb from "../../../components/block-breadcrumb";
import DefaultBanner from "./default";
import InformationalBanner from "./informational";
import AnnouncementBanner from "./announcement";
import LaunchBanner from "./launch";
import CTABanner from "./cta";

const AllBanners: FC = function () {
  return (
    <>
      <BlockPageBreadcrumb
        title="Banner"
        description="The banner component can be used to show extra information or enable interactions with the user without affecting the main content area of the website."
      />
      <BlockSection
        title="Default banner"
        description="Use this example of a dismissable banner component to show extra information relative to the main content area of the page based on a sticky positition."
        githubLink="https://github.com/themesberg/flowbite-react-blocks/blob/main/pages/marketing-ui/banners/default.tsx"
      >
        <DefaultBanner />
      </BlockSection>
      <BlockSection
        title="Informational banner"
        description="This example can be used to show informational context such as upcoming maintenance of the website positioned to the top side of the page."
        githubLink="https://github.com/themesberg/flowbite-react-blocks/blob/main/pages/marketing-ui/banners/list-with-heading.tsx"
      >
        <InformationalBanner />
      </BlockSection>
      <BlockSection
        title="Announcement banner"
        description="Use this example of a banner component to announce new features or changes to the website including a badge, description text and CTA link."
        githubLink="https://github.com/themesberg/flowbite-react-blocks/blob/main/pages/marketing-ui/banners/centered-posts.tsx"
      >
        <AnnouncementBanner />
      </BlockSection>
      <BlockSection
        title="Launch banner"
        description="This example can be used if you launched a new feature or product on your website by providing the logo and a CTA link."
        githubLink="https://github.com/themesberg/flowbite-react-blocks/blob/main/pages/marketing-ui/banners/card-with-image.tsx"
      >
        <LaunchBanner />
      </BlockSection>
      <BlockSection
        title="CTA banner"
        description="Get started with this example of a banner component to also show a CTA button such as booking a call or signing up for a demo of a product."
        githubLink="https://github.com/themesberg/flowbite-react-blocks/blob/main/pages/marketing-ui/banners/featured-post.tsx"
      >
        <CTABanner />
      </BlockSection>
    </>
  );
};

export default AllBanners;
