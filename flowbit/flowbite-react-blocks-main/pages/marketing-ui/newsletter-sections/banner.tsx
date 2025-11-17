import { Banner, Button, Label, TextInput } from "flowbite-react";
import { HiMail } from 'react-icons/hi';
import type { FC } from "react";

const BannerEmailSignUpNewsletterSection: FC = function () {
  return (
    <Banner>
      <div className="flex items-start w-full px-4 py-3 border border-b border-gray-200 sm:justify-between bg-white dark:border-gray-700 dark:bg-gray-800">
        <div className="items-center justify-center w-full sm:flex">
          <p className="mb-4 font-medium text-gray-500 sm:mb-0 dark:text-white md:mb-0">
            Subscribe to get updates!
          </p>
          <form action="#" className="sm:pl-10">
            <div className="flex items-center md:mx-auto sm:space-y-0">
              <div className="relative w-full mr-3">
                <Label
                  htmlFor="email"
                  className="block mb-2 text-sm font-medium text-gray-900 sr-only dark:text-gray-300"
                >
                  Email address
                </Label>
                <TextInput
                  id="email"
                  icon={HiMail}
                  placeholder="Your email"
                  required
                  type="email"
                  theme={
                    {
                      field: {
                        base: "w-full md:w-80"
                      }
                    }
                  }
                />
              </div>
              <div>
                <Button type="submit">Subscribe</Button>
              </div>
            </div>
          </form>
        </div>
        <Banner.CollapseButton color="gray" className="border-0 bg-transparent">
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
            ></path>
          </svg>
        </Banner.CollapseButton>
      </div>
    </Banner>
  );
};

export default BannerEmailSignUpNewsletterSection;
