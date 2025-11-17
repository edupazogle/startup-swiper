import { Button, Tooltip } from "flowbite-react";
import type { FC } from "react";

const ProjectPortfolioAlternateSections: FC = function () {
  return (
    <section className="bg-white dark:bg-gray-900 antialiased">
      <div className="max-w-screen-xl px-4 py-8 mx-auto lg:px-6 sm:py-16 lg:py-24">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-extrabold leading-tight tracking-tight text-gray-900 sm:text-4xl dark:text-white">
            Our work
          </h2>
          <p className="mt-4 text-base font-normal text-gray-500 sm:text-xl dark:text-gray-400">
            Flowbite helps you connect with friends, family and communities of
            people who share your interests.
          </p>
        </div>
        <div className="mt-12 space-y-16 sm:mt-16">
          <div className="flex flex-col lg:items-center lg:flex-row gap-y-8 sm:gap-y-12 lg:gap-x-16 xl:gap-x-24">
            <div>
              <img
                className="object-cover w-full rounded-lg shadow-lg dark:hidden"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/case-study/flowbite-dashboard.jpg"
                alt=""
              />
              <img
                className="object-cover w-full rounded-lg shadow-lg dark:block hidden"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/case-study/flowbite-dashboard-dark.jpg"
                alt=""
              />
            </div>
            <div className="w-full space-y-6 lg:max-w-lg shrink-0 xl:max-w-2xl">
              <div className="space-y-3">
                <h3 className="text-3xl font-bold leading-tight text-gray-900 sm:text-4xl dark:text-white">
                  Flowbite's dashboard
                </h3>
                <a
                  href="https://flowbite.com"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  https://flowbite.com
                  <svg
                    aria-hidden="true"
                    className="w-5 h-5 ml-2.5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                  </svg>
                </a>
                <p className="text-base font-normal text-gray-500 sm:text-lg dark:text-gray-400">
                  Flowbite helps you connect with friends, family and
                  communities of people who share your interests. Connecting
                  with your friends and family as well as discovering new ones
                  is easy with features like Groups.
                </p>
              </div>
              <div className="flex items-center gap-2.5">
                <Tooltip content="HTML5">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="CSS3">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/css-3.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="JavaScript">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/javascript.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="TypeScript">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/typescript.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button>
                View case study
                <svg
                  aria-hidden="true"
                  className="w-5 h-5 ml-2 -mr-1"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </Button>
            </div>
          </div>
          <div className="flex flex-col lg:items-center lg:flex-row gap-y-8 sm:gap-y-12 lg:gap-x-16 xl:gap-x-24">
            <div className="lg:order-2">
              <img
                className="object-cover w-full rounded-lg shadow-lg dark:hidden"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/case-study/agency-landing-page.jpg"
                alt=""
              />
              <img
                className="object-cover w-full rounded-lg shadow-lg dark:block hidden"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/case-study/agency-landing-page-dark.jpg"
                alt=""
              />
            </div>
            <div className="w-full space-y-6 lg:max-w-lg shrink-0 xl:max-w-2xl lg:order-1">
              <div className="space-y-3">
                <h3 className="text-3xl font-bold leading-tight text-gray-900 sm:text-4xl dark:text-white">
                  Agency Landing Page
                </h3>
                <a
                  href="https://themesberg.com"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  https://themesberg.com
                  <svg
                    aria-hidden="true"
                    className="w-5 h-5 ml-2.5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                  </svg>
                </a>
                <p className="text-base font-normal text-gray-500 sm:text-lg dark:text-gray-400">
                  Flowbite helps you connect with friends, family and
                  communities of people who share your interests. Connecting
                  with your friends and family as well as discovering new ones
                  is easy with features like Groups.
                </p>
              </div>
              <div className="flex items-center gap-2.5">
                <Tooltip content="WordPress">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/wordpress.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="CSS3">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/css-3.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="WooCommerce">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/woocommerce.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button>
                View case study
                <svg
                  aria-hidden="true"
                  className="w-5 h-5 ml-2 -mr-1"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </Button>
            </div>
          </div>
          <div className="flex flex-col lg:items-center lg:flex-row gap-y-8 sm:gap-y-12 lg:gap-x-16 xl:gap-x-24">
            <div>
              <img
                className="object-cover w-full rounded-lg shadow-lg dark:hidden"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/case-study/mail-management-system.jpg"
                alt=""
              />
              <img
                className="object-cover w-full rounded-lg shadow-lg dark:block hidden"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/case-study/mail-management-system-dark.jpg"
                alt=""
              />
            </div>
            <div className="w-full space-y-6 lg:max-w-lg shrink-0 xl:max-w-2xl">
              <div className="space-y-3">
                <h3 className="text-3xl font-bold leading-tight text-gray-900 sm:text-4xl dark:text-white">
                  Mail management system
                </h3>
                <a
                  href="https://ui.glass"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  https://ui.glass
                  <svg
                    aria-hidden="true"
                    className="w-5 h-5 ml-2.5"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                    <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                  </svg>
                </a>
                <p className="text-base font-normal text-gray-500 sm:text-lg dark:text-gray-400">
                  Flowbite helps you connect with friends, family and
                  communities of people who share your interests. Connecting
                  with your friends and family as well as discovering new ones
                  is easy with features like Groups.
                </p>
              </div>
              <div className="flex items-center gap-2.5">
                <Tooltip content="TypeScript">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/typescript.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Java">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/java.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="React">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/react.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Amazon Web Services">
                  <img
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/amazon-web-services.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button>
                View case study
                <svg
                  aria-hidden="true"
                  className="w-5 h-5 ml-2 -mr-1"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProjectPortfolioAlternateSections;
