import { Badge, Banner } from "flowbite-react";
import type { FC } from "react";
import { HiX } from "react-icons/hi";

const AnnouncementBanner: FC = function () {
  return (
    <Banner>
      <div className="flex w-full items-center justify-between border border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
        <div className="mx-auto flex items-center gap-x-3">
          <Badge className="w-fit">New</Badge>
          <p className="text-sm font-medium text-gray-900 dark:text-white md:my-0">
            We have launched Flowbite Blocks including over 120+ website
            sections!
          </p>
          <a
            href="#"
            className="ml-0 inline-flex items-center text-sm font-medium text-primary-600 hover:underline dark:text-primary-500"
          >
            Check it out!
          </a>
        </div>
        <Banner.CollapseButton
          color="gray"
          className="border-0 bg-transparent px-0"
        >
          <HiX className="h-4 w-4" />
        </Banner.CollapseButton>
      </div>
    </Banner>
  );
};

export default AnnouncementBanner;
