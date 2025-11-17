import { Button, Label, Radio } from "flowbite-react";
import type { FC } from "react";

const ChooseAccountTypeUserOnboarding: FC = function () {
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
                className="w-8 h-8 mr-2"
                src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg"
                alt=""
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
            <h2 className="mb-1 text-2xl font-semibold">Your selected plan</h2>
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
                  className="w-8 h-8 mr-2"
                  src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg"
                  alt=""
                />
                <span className="text-gray-900 dark:text-white">Flowbite</span>
              </a>
            </div>
            <ol className="flex items-center mb-6 text-sm font-medium text-center text-gray-500 dark:text-gray-400 lg:mb-12 sm:text-base">
              <li className="flex items-center after:content-[''] after:w-12 after:h-1 after:border-b after:border-gray-200 after:border-1 after:hidden sm:after:inline-block after:mx-6 xl:after:mx-10 dark:after:border-gray-700">
                <div className="flex items-center sm:block after:content-['/'] sm:after:hidden after:mx-2 after:after:text-gray-200 dark:after:text-gray-500">
                  <div className="mr-2 sm:mb-2 sm:mx-auto">1</div>
                  Personal <span className="hidden sm:inline-flex">Info</span>
                </div>
              </li>
              <li className="flex items-center after:content-[''] after:w-12 after:h-1 after:border-b after:border-gray-200 after:border-1 after:hidden sm:after:inline-block after:mx-6 xl:after:mx-10 dark:after:border-gray-700">
                <div className="flex items-center sm:block after:content-['/'] sm:after:hidden after:mx-2 after:after:text-gray-200 dark:after:text-gray-500">
                  <div className="mr-2 sm:mb-2 sm:mx-auto">2</div>
                  Account <span className="hidden sm:inline-flex">Info</span>
                </div>
              </li>
              <li className="flex items-center sm:block">
                <div className="mr-2 sm:mb-2 sm:mx-auto">3</div>
                Confirmation
              </li>
            </ol>
            <h1 className="mb-4 text-2xl font-extrabold leading-tight tracking-tight text-gray-900 sm:mb-6 dark:text-white">
              Tell us about yourself
            </h1>
            <p className="mb-4 text-lg text-gray-500 dark:text-gray-400">
              What is your profession?
            </p>
            <ul className="mb-6 space-y-4 sm:space-y-6">
              <li>
                <Radio
                  id="designer"
                  name="profession"
                  value="designer"
                  className="hidden peer"
                  required
                />
                <Label
                  htmlFor="designer"
                  className="text-base inline-flex items-center justify-center w-full p-5 text-gray-500 border-2 border-gray-200 rounded-lg cursor-pointer dark:hover:text-gray-300 dark:border-gray-700 dark:peer-checked:text-primary-500 peer-checked:border-primary-600 peer-checked:text-primary-600 bg-gray-50 hover:text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:bg-gray-800 dark:hover:bg-gray-700"
                >
                  <svg
                    className="w-6 h-6 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M4 2a2 2 0 00-2 2v11a3 3 0 106 0V4a2 2 0 00-2-2H4zm1 14a1 1 0 100-2 1 1 0 000 2zm5-1.757l4.9-4.9a2 2 0 000-2.828L13.485 5.1a2 2 0 00-2.828 0L10 5.757v8.486zM16 18H9.071l6-6H16a2 2 0 012 2v2a2 2 0 01-2 2z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="w-full">I’m a Designer</span>
                  <svg
                    className="w-6 h-6 ml-3"
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
                </Label>
              </li>
              <li>
                <Radio
                  id="developer"
                  name="profession"
                  value="developer"
                  className="hidden peer"
                />
                <Label
                  htmlFor="developer"
                  className="text-base inline-flex items-center justify-center w-full p-5 text-gray-500 border-2 border-gray-200 rounded-lg cursor-pointer dark:hover:text-gray-300 dark:border-gray-700 dark:peer-checked:text-primary-500 peer-checked:border-primary-600 peer-checked:text-primary-600 bg-gray-50 hover:text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:bg-gray-800 dark:hover:bg-gray-700"
                >
                  <svg
                    className="w-6 h-6 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="w-full">I’m a Developer</span>
                  <svg
                    className="w-6 h-6 ml-3"
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
                </Label>
              </li>
            </ul>
            <Button className="w-full py-2">Next: Account Info</Button>
            <p className="mt-4 text-sm text-gray-900 dark:text-white font-medium">
              Already have an account?&nbsp;
              <a
                href="#"
                className="font-medium text-primary-600 hover:underline dark:text-primary-500"
              >
                Login here
              </a>
              .
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ChooseAccountTypeUserOnboarding;
