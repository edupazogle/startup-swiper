import { Badge, Tabs, Timeline } from "flowbite-react";
import type { FC } from "react";

const EventScheduleTabs: FC = function () {
  return (
    <section className="bg-white dark:bg-gray-900 antialiased">
      <div className="max-w-screen-xl px-4 py-8 mx-auto lg:px-6 sm:py-16 lg:py-24">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl font-extrabold leading-tight tracking-tight text-gray-900 dark:text-white">
            The schedule
          </h2>
        </div>
        <div className="flex justify-center mt-8 lg:mt-12">
          <Tabs.Group
            style="pills"
            theme={{
              tablist: {
                styles: {
                  pills:
                    "flex-wrap justify-center font-medium text-sm text-gray-500 dark:text-gray-400 space-x-2",
                },
                tabitem: {
                  base: "flex items-center justify-center p-4 rounded-3xl text-sm font-medium first:ml-0 disabled:cursor-not-allowed disabled:text-gray-400 disabled:dark:text-gray-500 focus:ring-4 focus:ring-blue-300 focus:outline-none",
                  styles: {
                    pills: {
                      active: {
                        on: "bg-blue-600 text-white",
                        off: "hover:text-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 dark:hover:text-white",
                      },
                    },
                  },
                },
              },
            }}
          >
            <Tabs.Item active title="Day 1: Wednesday, Oct 12th">
              <Timeline className="border-0">
                <div className="grid max-w-5xl grid-cols-1 p-5 mx-auto border border-gray-100 rounded-lg bg-gray-50 sm:grid-cols-2 dark:bg-gray-800 dark:border-gray-700">
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        9:00 - 10:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Opening remarks
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/jese-leos.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Jese Leos
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CEO &amp; Co Founder Bergside LLC
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        10:00 - 11:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Women in Streaming Media Networking
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/leslie-livingston.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Leslie Livingston
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CEO &amp; Co Founder Meta
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        11:00 - 12:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Bergside LLC: Controlling the video traffic flows
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/lana-byrd.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Lana Byrd
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Video Engineer
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        13:00 - 14:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        The importance of platform optimisation in times of
                        expensive ads
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/joseph-mcfall.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Joseph McFall
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Engineer at Google
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        12:00 - 13:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Coffee &amp; networking
                      </a>
                    </Timeline.Title>
                    <div>
                      <p className="text-base font-medium text-gray-500 dark:text-gray-400">
                        Sponsors:
                      </p>
                      <div className="flex flex-wrap items-center mt-2 gap-x-6 gap-y-4 max-w-xs">
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/slack-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/salesforce-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/google-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/sap-grayscale.svg"
                          alt=""
                        />
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        14:00 - 15:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Flowbite - An Open Framework for Forensic Watermarking
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/michael-gough.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Micheal Gough
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CTO at Flowbite
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/bonnie-green.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Karen Nelson
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          React developer at Flowbite
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        15:00 - 16:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Updates from the Open Source Multimedia community
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/robert-brown.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Robert Brown
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Videolan
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        14:00 - 15:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Exploring the balance between customer acquisition and
                        retention
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/helene-engels.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Helene Engels
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Senior VP Amazon
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/roberta-casas.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Roberta Casas
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Head Designer Amazon
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r py-5 border-gray-200 dark:border-gray-700">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        17:00 - 18:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Scaling your brand from €0 to multimillion euros
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/thomas-lean.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Thomas Lean
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          COO Salesforce
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/neil-sims.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Neil Sims
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CTO Salesforce
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/bonnie-green.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Bonnie Green
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Python Developer
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        18:00 - 20:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Drinks &amp; networking
                      </a>
                    </Timeline.Title>
                    <div>
                      <p className="text-base font-medium text-gray-500 dark:text-gray-400">
                        Sponsors:
                      </p>
                      <div className="flex flex-wrap items-center mt-2 gap-x-6 gap-y-4 max-w-xs">
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/google-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/sap-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/slack-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/salesforce-grayscale.svg"
                          alt=""
                        />
                      </div>
                    </div>
                  </Timeline.Item>
                </div>
              </Timeline>
            </Tabs.Item>
            <Tabs.Item title="Day 2: Thursday, Oct 13th">
              <Timeline className="border-0">
                <div className="grid max-w-5xl grid-cols-1 p-5 mx-auto border border-gray-100 rounded-lg bg-gray-50 sm:grid-cols-2 dark:bg-gray-800 dark:border-gray-700">
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        18:00 - 20:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Drinks &amp; networking
                      </a>
                    </Timeline.Title>
                    <div>
                      <p className="text-base font-medium text-gray-500 dark:text-gray-400">
                        Sponsors:
                      </p>
                      <div className="flex flex-wrap items-center mt-2 gap-x-6 gap-y-4 max-w-xs">
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/google-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/sap-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/slack-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/salesforce-grayscale.svg"
                          alt=""
                        />
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        10:00 - 11:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Women in Streaming Media Networking
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/leslie-livingston.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Leslie Livingston
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CEO &amp; Co Founder Meta
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        14:00 - 15:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Flowbite - An Open Framework for Forensic Watermarking
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/michael-gough.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Micheal Gough
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CTO at Flowbite
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/bonnie-green.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Karen Nelson
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          React developer at Flowbite
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        13:00 - 14:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        The importance of platform optimisation in times of
                        expensive ads
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/joseph-mcfall.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Joseph McFall
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Engineer at Google
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        12:00 - 13:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Coffee &amp; networking
                      </a>
                    </Timeline.Title>
                    <div>
                      <p className="text-base font-medium text-gray-500 dark:text-gray-400">
                        Sponsors:
                      </p>
                      <div className="flex flex-wrap items-center mt-2 gap-x-6 gap-y-4 max-w-xs">
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/slack-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/google-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/sap-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/salesforce-grayscale.svg"
                          alt=""
                        />
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        14:00 - 15:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Exploring the balance between customer acquisition and
                        retention
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/helene-engels.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Helene Engels
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Senior VP Amazon
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/roberta-casas.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Roberta Casas
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Head Designer Amazon
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        15:00 - 16:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Updates from the Open Source Multimedia community
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/robert-brown.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Robert Brown
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Videolan
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        11:00 - 12:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Bergside LLC: Controlling the video traffic flows
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/lana-byrd.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Lana Byrd
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Video Engineer
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        17:00 - 18:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Scaling your brand from €0 to multimillion euros
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/thomas-lean.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Thomas Lean
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          COO Salesforce
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/neil-sims.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Neil Sims
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CTO Salesforce
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/bonnie-green.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Bonnie Green
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Python Developer
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        9:00 - 10:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        <a href="#" className="hover:underline">
                          Opening remarks
                        </a>
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/jese-leos.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Jese Leos
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CEO &amp; Co Founder Bergside LLC
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                </div>
              </Timeline>
            </Tabs.Item>
            <Tabs.Item title="Day 3: Friday, Oct 14th">
              <Timeline className="border-0">
                <div className="grid max-w-5xl grid-cols-1 p-5 mx-auto border border-gray-100 rounded-lg bg-gray-50 sm:grid-cols-2 dark:bg-gray-800 dark:border-gray-700">
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        10:00 - 11:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        <a href="#" className="hover:underline">
                          Women in Streaming Media Networking
                        </a>
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/leslie-livingston.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Leslie Livingston
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CEO &amp; Co Founder Meta
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        9:00 - 10:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Opening remarks
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/jese-leos.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Jese Leos
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CEO &amp; Co Founder Bergside LLC
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        11:00 - 12:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Bergside LLC: Controlling the video traffic flows
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/lana-byrd.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Lana Byrd
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Video Engineer
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        13:00 - 14:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        The importance of platform optimisation in times of
                        expensive ads
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/joseph-mcfall.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Joseph McFall
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Engineer at Google
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        14:00 - 15:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Flowbite - An Open Framework for Forensic Watermarking
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/michael-gough.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Micheal Gough
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CTO at Flowbite
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/bonnie-green.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Karen Nelson
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          React developer at Flowbite
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        12:00 - 13:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Coffee &amp; networking
                      </a>
                    </Timeline.Title>
                    <div>
                      <p className="text-base font-medium text-gray-500 dark:text-gray-400">
                        Sponsors:
                      </p>
                      <div className="flex flex-wrap items-center mt-2 gap-x-6 gap-y-4 max-w-xs">
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/google-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/sap-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/slack-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/salesforce-grayscale.svg"
                          alt=""
                        />
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        15:00 - 16:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Updates from the Open Source Multimedia community
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/robert-brown.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Robert Brown
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Videolan
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 md:border-b border-gray-200 dark:border-gray-700 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        14:00 - 15:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Exploring the balance between customer acquisition and
                        retention
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/helene-engels.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Helene Engels
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Senior VP Amazon
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/roberta-casas.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Roberta Casas
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Head Designer Amazon
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:border-r py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        17:00 - 18:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Scaling your brand from €0 to multimillion euros
                      </a>
                    </Timeline.Title>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/thomas-lean.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Thomas Lean
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          COO Salesforce
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/neil-sims.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Neil Sims
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          CTO Salesforce
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <img
                        className="object-cover w-12 h-12 rounded-full shrink-0"
                        src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/bonnie-green.png"
                        alt=""
                      />
                      <div>
                        <p className="text-lg font-medium leading-tight text-gray-900 dark:text-white">
                          Bonnie Green
                        </p>
                        <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                          Python Developer
                        </p>
                      </div>
                    </div>
                  </Timeline.Item>
                  <Timeline.Item className="ml-0 space-y-3 mb-0 md:pl-5 py-5">
                    <Timeline.Time>
                      <Badge className="w-fit">
                        <svg
                          aria-hidden="true"
                          className="w-3 h-3 mr-1"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                        18:00 - 20:00
                      </Badge>
                    </Timeline.Time>
                    <Timeline.Title>
                      <a href="#" className="hover:underline">
                        Drinks &amp; networking
                      </a>
                    </Timeline.Title>
                    <div>
                      <p className="text-base font-medium text-gray-500 dark:text-gray-400">
                        Sponsors:
                      </p>
                      <div className="flex flex-wrap items-center mt-2 gap-x-6 gap-y-4 max-w-xs">
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/google-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/sap-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-5"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/slack-grayscale.svg"
                          alt=""
                        />
                        <img
                          className="object-contain w-auto h-7"
                          src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/salesforce-grayscale.svg"
                          alt=""
                        />
                      </div>
                    </div>
                  </Timeline.Item>
                </div>
              </Timeline>
            </Tabs.Item>
          </Tabs.Group>
        </div>
        <div className="mt-8 text-center">
          <a
            href="#"
            title=""
            className="inline-flex items-center text-lg font-medium text-primary-600 hover:underline dark:text-primary-500"
          >
            Buy tickets
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
    </section>
  );
};

export default EventScheduleTabs;
