import { Badge, Button } from "flowbite-react";
import type { FC } from "react";

const DefaultProjectPortfolio: FC = function () {
  return (
    <section className="bg-white dark:bg-gray-900 antialiased">
      <div className="max-w-screen-xl px-4 py-8 mx-auto lg:px-6 sm:py-16 lg:py-24">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-extrabold leading-tight tracking-tight text-gray-900 sm:text-4xl dark:text-white">
            Our work
          </h2>
          <p className="mt-4 text-base font-normal text-gray-500 sm:text-xl dark:text-gray-400">
            Crafted with skill and care to help our clients grow their business!
          </p>
        </div>
        <div className="grid grid-cols-1 mt-12 text-center sm:mt-16 gap-x-20 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
          <div className="space-y-4">
            <Badge color="gray" className="inline-flex">
              Alphabet Inc.
            </Badge>
            <h3 className="text-2xl font-bold leading-tight text-gray-900 dark:text-white">
              Official website
            </h3>
            <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
              Flowbite helps you connect with friends, family and communities of
              people who share your interests.
            </p>
            <Button className="inline-flex">
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
          <div className="space-y-4">
            <Badge color="gray" className="inline-flex">
              Microsoft Corp.
            </Badge>
            <h3 className="text-2xl font-bold leading-tight text-gray-900 dark:text-white">
              Management system
            </h3>
            <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
              Flowbite helps you connect with friends, family and communities of
              people who share your interests.
            </p>
            <Button className="inline-flex">
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
          <div className="space-y-4">
            <Badge color="gray" className="inline-flex">
              Adobe Inc.
            </Badge>
            <h3 className="text-2xl font-bold leading-tight text-gray-900 dark:text-white">
              Logo design
            </h3>
            <p className="text-lg font-normal text-gray-500 dark:text-gray-400">
              Flowbite helps you connect with friends, family and communities of
              people who share your interests.
            </p>
            <Button className="inline-flex">
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
    </section>
  );
};

export default DefaultProjectPortfolio;
