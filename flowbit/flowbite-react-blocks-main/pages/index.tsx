import { Badge } from "flowbite-react";
import type { FC } from "react";
import { Link } from "react-router-dom";
import categoriesOfBlocks from "../data/blocks-categories.json";

const HomePage: FC = function () {
  return (
    <div className="p-4 dark:bg-gray-900 max-w-screen-2xl mx-auto">
      <h1 className="mb-2 text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white">
        Flowbite Blocks in React
      </h1>
      <p className="mb-8 text-lg text-gray-500 dark:text-gray-400 max-w-3xl">
        Get started with 185 premium UI components based on Tailwind CSS, Flowbite, and React with support for TypeScript to upgrade your development stack and collaborate with designers to build websites even faster.
      </p>
      <div className="lg:text-center">
        <BlockCategoryCardsSection />
      </div>
    </div>
  );
};

const BlockCategoryCardsSection: FC = function () {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      {categoriesOfBlocks.map(
        ({
          categorySlug,
          categoryTitle,
          iconDark,
          iconLight,
          numComponents,
          slug,
          title,
        }) => (
          <Link
            key={title}
            to={`${categorySlug}/${slug}`}
            className="dark:hover:shadow-lg-light h-64 cursor-pointer rounded-lg border border-gray-100 bg-white hover:border-white hover:shadow-lg dark:border-gray-700 dark:bg-gray-900 dark:hover:border-gray-600 md:h-80"
          >
            <article className="flex items-center justify-between rounded-t-md border-b border-gray-200 bg-gray-50 px-5 py-2.5 dark:border-gray-700 dark:bg-gray-700">
              <div className="text-left">
                <h2 className="flex items-center text-base font-medium text-gray-900 dark:text-white">
                  {title}
                </h2>
                <p className="text-gray-500">{numComponents} components</p>
              </div>
              <div className="text-gray-900 dark:text-white">
                <Badge color="success" className="px-2">
                  {categoryTitle}
                </Badge>
              </div>
            </article>
            <div className="relative flex h-[calc(100%_-_4rem)] items-center justify-center">
              {iconDark && (
                <div className="relative hidden h-auto w-full text-center dark:block">
                  <img
                    alt={`${title} thumbnail dark mode`}
                    src={iconDark}
                    className="mx-auto h-44 max-w-full md:h-52"
                  />
                </div>
              )}
              {iconLight && (
                <div className="relative h-auto w-full text-center dark:hidden">
                  <img
                    alt={`${title} thumbnail dark mode`}
                    src={iconLight}
                    className="mx-auto h-44 max-w-full md:h-52"
                  />
                </div>
              )}
            </div>
          </Link>
        )
      )}
    </div>
  );
};

export default HomePage;
