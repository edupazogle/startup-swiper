import { Button, Carousel, Tooltip } from "flowbite-react";
import type { FC } from "react";

const ProjectPortfolioCarousel: FC = function () {
  return (
    <section className="bg-white dark:bg-gray-900 antialiased">
      <div className="max-w-screen-xl px-4 py-8 mx-auto lg:px-6 sm:py-16 lg:py-24">
        <div className="max-w-2xl space-y-6">
          <div>
            <p className="text-lg font-medium leading-none text-primary-600 dark:text-primary-500">
              Trusted Worldwide
            </p>
            <h2 className="mt-3 text-3xl font-extrabold leading-tight tracking-tight text-gray-900 sm:text-4xl dark:text-white">
              Trusted by over 100 companies and 10,000+ freelancers
            </h2>
            <p className="mt-4 text-base font-normal text-gray-500 sm:text-xl dark:text-gray-400">
              Our rigorous security and compliance standards are at the heart of
              all we do. We work tirelessly to protect you and your customers.
            </p>
          </div>
          <div className="space-y-4">
            <a
              href="#"
              title=""
              className="flex items-center text-base font-medium text-primary-600 hover:underline dark:text-primary-500"
            >
              View all projects
              <svg
                aria-hidden="true"
                className="w-5 h-5 ml-2"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </a>
            <a
              href="#"
              title=""
              className="flex items-center text-base font-medium text-primary-600 hover:underline dark:text-primary-500"
            >
              View all testimonials
              <svg
                aria-hidden="true"
                className="w-5 h-5 ml-2"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </a>
          </div>
        </div>
        <Carousel
          leftControl={
            <svg
              aria-hidden="true"
              className="w-7 h-7 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                d="M7.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l2.293 2.293a1 1 0 010 1.414z"
                clipRule="evenodd"
              />
            </svg>
          }
          rightControl={
            <svg
              aria-hidden="true"
              className="w-7 h-7 ml-2"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          }
          theme={{
            root: {
              leftControl: "absolute -bottom-8 right-1/2 [&_svg]:text-gray-500 [&_svg]:hover:text-gray-900 [&_svg]:dark:hover:text-white",
              rightControl: "absolute -bottom-8 left-1/2 [&_svg]:text-gray-500 [&_svg]:hover:text-gray-900 [&_svg]:dark:hover:text-white",
            },
            indicators: {
              "base": "d-none"
            }
          }}
          className="mt-8 sm:mt-12 lg:mt-16 h-[400px]"
        >
          <div className="grid grid-cols-1 gap-20 sm:grid-cols-2 xl:grid-cols-3">
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/ford.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Official website
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="Flowbite">
                  <img
                    data-tooltip-target="tooltip-logo-flowbite"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/flowbite.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    data-tooltip-target="tooltip-logo-tailwind-css"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    data-tooltip-target="tooltip-logo-html5"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="CSS3">
                  <img
                    data-tooltip-target="tooltip-logo-css3"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/css-3.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/fedex.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Management system
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="TypeScript">
                  <img
                    data-tooltip-target="tooltip-logo-typescript"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/typescript.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Java">
                  <img
                    data-tooltip-target="tooltip-logo-java"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/java.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    data-tooltip-target="tooltip-logo-tailwind-css"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="React">
                  <img
                    data-tooltip-target="tooltip-logo-react"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/react.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    data-tooltip-target="tooltip-logo-html5"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Amazon Web Services">
                  <img
                    data-tooltip-target="tooltip-logo-amazon-web-services"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/amazon-web-services.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/intel.svg"
                alt=""
              />

              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Logo design
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="Figma">
                  <img
                    data-tooltip-target="tooltip-logo-figma"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/figma.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Adobe Illustrator">
                  <img
                    data-tooltip-target="tooltip-logo-illustrator"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/illustrator.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-20 sm:grid-cols-2 xl:grid-cols-3">
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Official website
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="Flowbite">
                  <img
                    data-tooltip-target="tooltip-logo-flowbite"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/flowbite.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    data-tooltip-target="tooltip-logo-tailwind-css"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    data-tooltip-target="tooltip-logo-html5"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="CSS3">
                  <img
                    data-tooltip-target="tooltip-logo-css3"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/css-3.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/netflix.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Management system
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="TypeScript">
                  <img
                    data-tooltip-target="tooltip-logo-typescript"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/typescript.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Java">
                  <img
                    data-tooltip-target="tooltip-logo-java"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/java.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    data-tooltip-target="tooltip-logo-tailwind-css"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="React">
                  <img
                    data-tooltip-target="tooltip-logo-react"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/react.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    data-tooltip-target="tooltip-logo-html5"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Amazon Web Services">
                  <img
                    data-tooltip-target="tooltip-logo-amazon-web-services"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/amazon-web-services.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Logo design
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="Figma">
                  <img
                    data-tooltip-target="tooltip-logo-figma"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/figma.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Adobe Illustrator">
                  <img
                    data-tooltip-target="tooltip-logo-illustrator"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/illustrator.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-20 sm:grid-cols-2 xl:grid-cols-3">
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/ford.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Official website
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="Flowbite">
                  <img
                    data-tooltip-target="tooltip-logo-flowbite"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/flowbite.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    data-tooltip-target="tooltip-logo-tailwind-css"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    data-tooltip-target="tooltip-logo-html5"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="CSS3">
                  <img
                    data-tooltip-target="tooltip-logo-css3"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/css-3.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/fedex.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Management system
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="TypeScript">
                  <img
                    data-tooltip-target="tooltip-logo-typescript"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/typescript.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Java">
                  <img
                    data-tooltip-target="tooltip-logo-java"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/java.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    data-tooltip-target="tooltip-logo-tailwind-css"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="React">
                  <img
                    data-tooltip-target="tooltip-logo-react"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/react.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    data-tooltip-target="tooltip-logo-html5"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Amazon Web Services">
                  <img
                    data-tooltip-target="tooltip-logo-amazon-web-services"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/amazon-web-services.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/intel.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Logo design
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="Figma">
                  <img
                    data-tooltip-target="tooltip-logo-figma"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/figma.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Adobe Illustrator">
                  <img
                    data-tooltip-target="tooltip-logo-illustrator"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/illustrator.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-20 sm:grid-cols-2 xl:grid-cols-3">
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Official website
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="Flowbite">
                  <img
                    data-tooltip-target="tooltip-logo-flowbite"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/flowbite.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    data-tooltip-target="tooltip-logo-tailwind-css"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    data-tooltip-target="tooltip-logo-html5"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="CSS3">
                  <img
                    data-tooltip-target="tooltip-logo-css3"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/css-3.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/netflix.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Management system
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="TypeScript">
                  <img
                    data-tooltip-target="tooltip-logo-typescript"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/typescript.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Java">
                  <img
                    data-tooltip-target="tooltip-logo-java"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/java.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Tailwind CSS">
                  <img
                    data-tooltip-target="tooltip-logo-tailwind-css"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/tailwind-css.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="React">
                  <img
                    data-tooltip-target="tooltip-logo-react"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/react.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="HTML5">
                  <img
                    data-tooltip-target="tooltip-logo-html5"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/html5.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Amazon Web Services">
                  <img
                    data-tooltip-target="tooltip-logo-amazon-web-services"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/amazon-web-services.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
            <div className="space-y-4">
              <img
                className="object-contain w-auto h-12"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft.svg"
                alt=""
              />
              <div className="space-y-1">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Logo design
                </h3>
                <a
                  href="#"
                  title=""
                  className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
                >
                  Live preview
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
              </div>
              <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
                Flowbite helps you connect with friends, family and communities
                of people who share your interests.
              </p>
              <div className="flex items-center gap-2.5">
                <Tooltip content="Figma">
                  <img
                    data-tooltip-target="tooltip-logo-figma"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/figma.svg"
                    alt=""
                  />
                </Tooltip>
                <Tooltip content="Adobe Illustrator">
                  <img
                    data-tooltip-target="tooltip-logo-illustrator"
                    className="object-contain w-auto h-8"
                    src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/technologies/illustrator.svg"
                    alt=""
                  />
                </Tooltip>
              </div>
              <Button color="gray" href="#" theme={{
                  "color": { "gray": "text-gray-900 bg-white border border-gray-200 hover:bg-gray-50 hover:text-primary-600 focus:ring-primary-700 focus:text-primary-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700 focus:ring-2" },
                  "inner": { "base": "flex items-stretch transition-0" }
                  }} className="w-fit">
                View case study
              </Button>
            </div>
          </div>
        </Carousel>
      </div>
    </section>
  );
};

export default ProjectPortfolioCarousel;
