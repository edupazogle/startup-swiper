import { Banner, Button } from "flowbite-react";
import type { FC } from "react";

const CookieBanner: FC = function () {
  return (
    <Banner>
      <div className="relative w-full h-full md:h-auto">
        <div className="relative bg-white shadow dark:bg-gray-800">
          <div className="justify-between items-center p-5 lg:flex">
            <p className="mb-4 text-sm text-gray-500 dark:text-white lg:mb-0">
              We use our own cookies as well as third-party cookies on our
              websites to enhance your experience, analyze our traffic, and for
              security and marketing. Select "Accept All" to allow them to be
              used. Read our&nbsp;
              <a
                href="#"
                className="font-medium text-gray-900 hover:underline dark:text-white"
              >
                Cookie Policy
              </a>
              .
            </p>
            <div className="items-center space-y-4 sm:space-y-0 sm:space-x-4 sm:flex lg:pl-10 shrink-0">
              <a
                href="#"
                className="text-sm text-primary-600 dark:text-primary-500 hover:underline"
              >
                Manage settings
              </a>
              <Button>Block all cookies</Button>
              <Button>Accept all</Button>
              <Banner.CollapseButton
                color="gray"
                className="border-0 bg-transparent"
              >
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </Banner.CollapseButton>
            </div>
          </div>
        </div>
      </div>
    </Banner>
  );
};

export default CookieBanner;
