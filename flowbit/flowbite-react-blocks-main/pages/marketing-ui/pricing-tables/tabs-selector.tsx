import { Tabs } from "flowbite-react";
import { useState, type FC } from "react";

const TabsSelectorPricingCards: FC = function () {
  const [activeTab, setActiveTab] = useState("Standard");

  return (
    <section className="bg-white dark:bg-gray-900">
      <div className="py-8 px-4 mx-auto max-w-screen-xl lg:py-16 lg:px-6">
        <div className="bg-white rounded-lg divide-y divide-gray-200 shadow dark:divide-gray-700 lg:divide-y-0 lg:divide-x lg:grid lg:grid-cols-3 dark:bg-gray-800">
          <div className="col-span-2 p-6 lg:p-8">
            <h3 className="mb-4 text-lg font-medium text-gray-900 dark:text-white">
              Choose a pricing plan:
            </h3>
            <Tabs.Group
              style="fullWidth"
              onClick={() => {
                window.setTimeout(() => {
                  setActiveTab(
                    document.querySelector("[aria-selected=true]")?.innerHTML ??
                      ""
                  );
                }, 50);
              }}
            >
              <Tabs.Item title="Starter">
                <div className="mt-6 mb-2 font-medium text-gray-900 dark:text-white">
                  Starter details:
                </div>
                <p className="text-lg text-gray-500 dark:text-gray-400">
                  Plan pricing starts at 250 contacts. Select your audience size
                  to calculate your price. The monthly email send limit for
                  Standard plans is 12 times your maximum contact count.*.
                </p>
              </Tabs.Item>
              <Tabs.Item active title="Standard">
                <div className="mt-6 mb-2 font-medium text-gray-900 dark:text-white">
                  Standard details:
                </div>
                <p className="text-lg text-gray-500 dark:text-gray-400">
                  Plan pricing starts at 500 contacts. Select your audience size
                  to calculate your price. The monthly email send limit for
                  Standard plans is 12 times your maximum contact count.*.
                </p>
              </Tabs.Item>
              <Tabs.Item title="Premium">
                <div className="mt-6 mb-2 font-medium text-gray-900 dark:text-white">
                  Premium details:
                </div>
                <p className="text-lg text-gray-500 dark:text-gray-400">
                  Plan pricing starts at 1000 contacts. Select your audience
                  size to calculate your price. The monthly email send limit for
                  Standard plans is 12 times your maximum contact count.*.
                </p>
              </Tabs.Item>
              <Tabs.Item title="Enterprise">
                <div className="mt-6 mb-2 font-medium text-gray-900 dark:text-white">
                  Enterprise details:
                </div>
                <p className="text-lg text-gray-500 dark:text-gray-400">
                  Plan pricing starts at unlimited contacts. Select your
                  audience size to calculate your price. The monthly email send
                  limit for Standard plans is 12 times your maximum contact
                  count.*.
                </p>
              </Tabs.Item>
            </Tabs.Group>
          </div>
          <div className="flex p-6 lg:p-8">
            <div
              className={`self-center w-full ${
                activeTab === "Starter" ? "" : "hidden"
              }`}
            >
              <div className="mb-4 text-2xl font-semibold text-gray-900 dark:text-white">
                Starter plan
              </div>
              <div className="text-gray-500 dark:text-gray-400">
                Starts at
              </div>
              <div className="mb-4 text-5xl font-extrabold text-gray-900 dark:text-white">
                $49
              </div>
              <a
                href="#"
                className="flex justify-center text-white bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:ring-bue-200 dark:focus:ring-primary-900 font-medium rounded-lg text-sm px-5 py-2.5 text-center mb-4"
              >
                Buy now
              </a>
              <a
                href="#"
                className="flex items-center mb-4 font-medium text-primary-600 hover:text-primary-700 dark:text-primary-500"
              >
                View team pricing
                <svg
                  className="ml-2 w-5 h-5"
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
              </a>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                *To see the monthly email send limit included with your specific
                plan, click Calculate my price. If your plan's contact or email
                send limit is exceeded, you will be charged for overages.
              </p>
            </div>
            <div
              id="standard-plan"
              className={`self-center w-full ${
                activeTab === "Standard" ? "" : "hidden"
              }`}
            >
              <div className="mb-4 text-2xl font-semibold text-gray-900 dark:text-white">
                Standard plan
              </div>
              <div className="text-gray-500 dark:text-gray-400">
                Starts at
              </div>
              <div className="mb-4 text-5xl font-extrabold text-gray-900 dark:text-white">
                $99
              </div>
              <a
                href="#"
                className="flex justify-center text-white bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:ring-bue-200 dark:focus:ring-primary-900 font-medium rounded-lg text-sm px-5 py-2.5 text-center mb-4"
              >
                Buy now
              </a>
              <a
                href="#"
                className="flex items-center mb-4 font-medium text-primary-600 hover:text-primary-700 dark:text-primary-500"
              >
                View team pricing
                <svg
                  className="ml-2 w-5 h-5"
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
              </a>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                *To see the monthly email send limit included with your specific
                plan, click Calculate my price. If your plan's contact or email
                send limit is exceeded, you will be charged for overages.
              </p>
            </div>
            <div
              className={`self-center w-full ${
                activeTab === "Premium" ? "" : "hidden"
              }`}
            >
              <div className="mb-4 text-2xl font-semibold text-gray-900 dark:text-white">
                Premium plan
              </div>
              <div className="text-gray-500 dark:text-gray-400">
                Starts at
              </div>
              <div className="mb-4 text-5xl font-extrabold text-gray-900 dark:text-white">
                $149
              </div>
              <a
                href="#"
                className="flex justify-center text-white bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:ring-bue-200 dark:focus:ring-primary-900 font-medium rounded-lg text-sm px-5 py-2.5 text-center mb-4"
              >
                Buy now
              </a>
              <a
                href="#"
                className="flex items-center mb-4 font-medium text-primary-600 hover:text-primary-700 dark:text-primary-500"
              >
                View team pricing
                <svg
                  className="ml-2 w-5 h-5"
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
              </a>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                *To see the monthly email send limit included with your specific
                plan, click Calculate my price. If your plan's contact or email
                send limit is exceeded, you will be charged for overages.
              </p>
            </div>
            <div
              className={`self-center w-full ${
                activeTab === "Enterprise" ? "" : "hidden"
              }`}
            >
              <div className="mb-4 text-2xl font-semibold text-gray-900 dark:text-white">
                Enterprise plan
              </div>
              <div className="text-gray-500 dark:text-gray-400">
                Starts at
              </div>
              <div className="mb-4 text-5xl font-extrabold text-gray-900 dark:text-white">
                $249
              </div>
              <a
                href="#"
                className="flex justify-center text-white bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:ring-bue-200 dark:focus:ring-primary-900 font-medium rounded-lg text-sm px-5 py-2.5 text-center mb-4"
              >
                Buy now
              </a>
              <a
                href="#"
                className="flex items-center mb-4 font-medium text-primary-600 hover:text-primary-700 dark:text-primary-500"
              >
                View team pricing
                <svg
                  className="ml-2 w-5 h-5"
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
              </a>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                *To see the monthly email send limit included with your specific
                plan, click Calculate my price. If your plan's contact or email
                send limit is exceeded, you will be charged for overages.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TabsSelectorPricingCards;
