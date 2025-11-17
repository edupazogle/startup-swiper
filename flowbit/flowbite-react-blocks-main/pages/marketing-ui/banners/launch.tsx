import { Banner } from "flowbite-react";
import type { FC } from "react";
import { HiExternalLink, HiX } from "react-icons/hi";

const LaunchBanner: FC = function () {
  return (
    <Banner>
      <div className="flex w-full justify-between border border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800 lg:py-4">
        <div className="flex items-center md:mx-auto">
          <a
            href="#"
            className="mr-3 hidden items-center text-xl font-semibold text-gray-900 dark:text-white sm:flex"
          >
            <img
              alt=""
              src="https://flowbite.com/docs/images/logo.svg"
              className="mr-3"
            />
            Flowbite
          </a>
          <a
            href="#"
            className="flex items-center text-sm text-primary-600 hover:underline dark:text-primary-500"
          >
            We launched Marketing UI Blocks
            <HiExternalLink className="ml-2" />
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

export default LaunchBanner;
