import { Button } from "flowbite-react";
import type { FC } from "react";

const EmailVerificationSixDigitCode: FC = function () {
  return (
    <section className="py-8 bg-white dark:bg-gray-900 lg:py-0 px-4">
      <div className="lg:flex">
        <div className="hidden w-full max-w-md p-12 lg:h-screen lg:block bg-primary-600">
          <div className="flex items-center mb-8 space-x-4">
            <a
              href="#"
              className="flex items-center text-2xl font-semibold text-white"
            >
              <img
                alt=""
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg"
                className="w-8 h-8 mr-2"
              />
              Flowbite
            </a>
            <a
              href="#"
              className="inline-flex items-center text-sm font-medium text-primary-100 hover:text-white"
            >
              <svg
                className="w-6 h-6 mr-1"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fillRule="evenodd"
                  d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              Go back
            </a>
          </div>
          <div className="block p-8 text-white rounded-lg bg-primary-500">
            <h3 className="mb-1 text-2xl font-semibold">Your selected plan</h3>
            <p className="mb-4 text-primary-100 sm:text-lg">
              30-day free trial
            </p>
            <ul className="space-y-4 text-left">
              <li className="flex items-center space-x-3">
                <svg
                  className="flex-shrink-0 w-5 h-5 text-green-300"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Individual configuration</span>
              </li>
              <li className="flex items-center space-x-3">
                <svg
                  className="flex-shrink-0 w-5 h-5 text-green-300"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>No setup, or hidden fees</span>
              </li>
              <li className="flex items-center space-x-3">
                <svg
                  className="flex-shrink-0 w-5 h-5 text-green-300"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>
                  Team size: <span className="font-semibold">1 developer</span>
                </span>
              </li>
              <li className="flex items-center space-x-3">
                <svg
                  className="flex-shrink-0 w-5 h-5 text-green-300"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>
                  Premium support:&nbsp;
                  <span className="font-semibold">6 months</span>
                </span>
              </li>
              <li className="flex items-center space-x-3">
                <svg
                  className="flex-shrink-0 w-5 h-5 text-green-300"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>
                  Free updates: <span className="font-semibold">6 months</span>
                </span>
              </li>
            </ul>
          </div>
        </div>
        <div className="flex items-center mx-auto md:w-[42rem] md:px-8 xl:px-0">
          <div className="w-full">
            <div className="flex items-center justify-center mb-8 space-x-4 lg:hidden">
              <a href="#" className="flex items-center text-2xl font-semibold">
                <img
                  alt=""
                  className="w-8 h-8 mr-2"
                  src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg"
                />
                <span className="text-gray-900 dark:text-white">Flowbite</span>
              </a>
            </div>
            <ol className="flex items-center mb-6 text-sm font-medium text-center text-gray-500 dark:text-gray-400 lg:mb-12 sm:text-base">
              <li className="flex items-center text-primary-600 dark:text-primary-500 sm:after:content-[''] after:w-12 after:h-1 after:border-b after:border-gray-200 after:border-1 after:hidden sm:after:inline-block after:mx-6 xl:after:mx-10 dark:after:border-gray-700">
                <div className="flex md:flex-col items-center after:content-['/'] sm:after:hidden after:mx-2 after:after:text-gray-200 dark:after:text-gray-500">
                  <svg
                    className="w-4 h-4 mr-2 sm:mb-2 sm:w-6 sm:h-6 sm:mx-auto shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>
                    Personal <span className="hidden sm:inline-flex">Info</span>
                  </span>
                </div>
              </li>
              <li className="flex items-center text-primary-600 dark:text-primary-500 after:content-[''] after:w-12 after:h-1 after:border-b after:border-gray-200 after:border-1 after:hidden sm:after:inline-block after:mx-6 xl:after:mx-10 dark:after:border-gray-700">
                <div className="flex md:flex-col items-center after:content-['/'] sm:after:hidden after:mx-2 after:after:text-gray-200 dark:after:text-gray-500">
                  <svg
                    className="w-4 h-4 mr-2 sm:mb-2 sm:w-6 sm:h-6 sm:mx-auto shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>
                    Account <span className="hidden sm:inline-flex">Info</span>
                  </span>
                </div>
              </li>
              <li className="flex items-center sm:block">
                <div className="mr-2 sm:mb-2 sm:mx-auto">3</div>
                Confirmation
              </li>
            </ol>
            <h1 className="mb-2 text-2xl font-extrabold tracking-tight text-gray-900 leding-tight dark:text-white">
              Verify your email address
            </h1>
            <p className="text-gray-500 dark:text-gray-400">
              We emailed you a six-digit code to&nbsp;
              <span className="font-medium text-gray-900 dark:text-white">
                name@company.com
              </span>
              . Enter the code below to confirm your email address.
            </p>
            <form action="#">
              <div className="flex my-4 space-x-2 sm:space-x-4 md:my-6">
                <div>
                  <label htmlFor="code-1" className="sr-only">
                    First code
                  </label>
                  <input
                    id="code-1"
                    maxLength={1}
                    onKeyUp={() =>
                      (
                        document.querySelector("#code-2") as HTMLInputElement
                      )?.focus()
                    }
                    required
                    type="text"
                    className="block w-12 h-12 py-3 text-2xl font-extrabold text-center text-gray-900 bg-white border border-gray-300 rounded-lg sm:py-4 sm:text-4xl sm:w-16 sm:h-16 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                  />
                </div>
                <div>
                  <label htmlFor="code-2" className="sr-only">
                    Second code
                  </label>
                  <input
                    id="code-2"
                    maxLength={1}
                    onKeyUp={() =>
                      (
                        document.querySelector("#code-3") as HTMLInputElement
                      )?.focus()
                    }
                    type="text"
                    required
                    className="block w-12 h-12 py-3 text-2xl font-extrabold text-center text-gray-900 bg-white border border-gray-300 rounded-lg sm:py-4 sm:text-4xl sm:w-16 sm:h-16 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                  />
                </div>
                <div>
                  <label htmlFor="code-3" className="sr-only">
                    Third code
                  </label>
                  <input
                    type="text"
                    maxLength={1}
                    id="code-3"
                    onKeyUp={() =>
                      (
                        document.querySelector("#code-4") as HTMLInputElement
                      )?.focus()
                    }
                    className="block w-12 h-12 py-3 text-2xl font-extrabold text-center text-gray-900 bg-white border border-gray-300 rounded-lg sm:py-4 sm:text-4xl sm:w-16 sm:h-16 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                    required
                  />
                </div>
                <div>
                  <label htmlFor="code-4" className="sr-only">
                    Fourth code
                  </label>
                  <input
                    id="code-4"
                    maxLength={1}
                    onKeyUp={() =>
                      (
                        document.querySelector("#code-5") as HTMLInputElement
                      )?.focus()
                    }
                    required
                    type="text"
                    className="block w-12 h-12 py-3 text-2xl font-extrabold text-center text-gray-900 bg-white border border-gray-300 rounded-lg sm:py-4 sm:text-4xl sm:w-16 sm:h-16 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                  />
                </div>
                <div>
                  <label htmlFor="code-5" className="sr-only">
                    Fifth code
                  </label>
                  <input
                    id="code-5"
                    maxLength={1}
                    onKeyUp={() =>
                      (
                        document.querySelector("#code-6") as HTMLInputElement
                      )?.focus()
                    }
                    required
                    type="text"
                    className="block w-12 h-12 py-3 text-2xl font-extrabold text-center text-gray-900 bg-white border border-gray-300 rounded-lg sm:py-4 sm:text-4xl sm:w-16 sm:h-16 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                  />
                </div>
                <div>
                  <label htmlFor="code-6" className="sr-only">
                    Sixth code
                  </label>
                  <input
                    type="text"
                    maxLength={1}
                    id="code-6"
                    className="block w-12 h-12 py-3 text-2xl font-extrabold text-center text-gray-900 bg-white border border-gray-300 rounded-lg sm:py-4 sm:text-4xl sm:w-16 sm:h-16 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500"
                    required
                  />
                </div>
              </div>
              <p className="p-4 mb-4 text-sm text-gray-500 rounded-lg bg-gray-50 dark:text-gray-400 md:mb-6 dark:bg-gray-800">
                Make sure to keep this window open while checking your inbox.
              </p>
              <div className="grid grid-cols-2 gap-3">
                <Button color="gray" href="#" className="hover:text-primary-600 hover:bg-gray-100 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700">
                  Prev: Account Info
                </Button>
                <Button type="submit">
                  Verify account
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
};

export default EmailVerificationSixDigitCode;
