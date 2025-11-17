import { Button, Checkbox, Label, Select, TextInput } from "flowbite-react";
import type { FC } from "react";

const AccountDetailsUserOnboarding: FC = function () {
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
                  src="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/logo.svg"
                  className="w-8 h-8 mr-2"
                />
                <span className="text-gray-900 dark:text-white">Flowbite</span>
              </a>
            </div>
            <ol className="flex items-center mb-6 text-sm font-medium text-center text-gray-500 dark:text-gray-400 lg:mb-12 sm:text-base">
              <li className="flex items-center text-primary-600 dark:text-primary-500 sm:after:content-[''] after:w-12 after:h-1 after:border-b after:border-gray-200 after:border-1 after:hidden sm:after:inline-block after:mx-6 xl:after:mx-10 dark:after:border-gray-700">
                <div className="flex md:flex-col items-center after:content-['/'] sm:after:hidden after:mx-2 after:after:text-gray-200 dark:after:text-gray-500">
                  <svg
                    className="w-4 h-4 mr-2 sm:mb-2 sm:w-6 sm:h-6 sm:mx-auto"
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
            <h1 className="mb-4 text-2xl font-extrabold tracking-tight text-gray-900 sm:mb-6 leding-tight dark:text-white">
              Account details
            </h1>
            <form action="#">
              <div className="grid gap-5 my-6 sm:grid-cols-2">
                <div>
                  <Label
                    htmlFor="full-name"
                    className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                  >
                    Full Name
                  </Label>
                  <TextInput
                    name="full-name"
                    id="full-name"
                    placeholder="Bonnie"
                    required
                  />
                </div>
                <div>
                  <Label
                    htmlFor="email"
                    className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                  >
                    Your email
                  </Label>
                  <TextInput
                    type="email"
                    name="email"
                    id="email"
                    placeholder="name@company.com"
                    required
                  />
                </div>
                <div>
                  <Label
                    htmlFor="password"
                    className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                  >
                    Password
                  </Label>
                  <TextInput
                    type="password"
                    name="password"
                    id="password"
                    placeholder="••••••••"
                    required
                  />
                </div>
                <div>
                  <Label
                    htmlFor="confirm-password"
                    className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                  >
                    Confirm password
                  </Label>
                  <TextInput
                    type="password"
                    name="confirm-password"
                    id="confirm-password"
                    placeholder="••••••••"
                    required
                  />
                </div>
                <div>
                  <Label
                    htmlFor="country"
                    className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                  >
                    Country
                  </Label>
                  <Select id="country">
                    <option selected>Choose your country</option>
                    <option value="USA">USA</option>
                    <option value="UK">United Kingdom</option>
                    <option value="CA">Canada</option>
                    <option value="FR">France</option>
                    <option value="DE">Germany</option>
                    <option value="ES">Spain</option>
                    <option value="JP">Japan</option>
                    <option value="AUS">Australia</option>
                  </Select>
                </div>
                <div>
                  <Label
                    htmlFor="phone-number"
                    className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                  >
                    Phone
                  </Label>
                  <TextInput
                    type="number"
                    name="phone-number"
                    id="phone-number"
                    placeholder="+123 567 890"
                    required
                  />
                </div>
              </div>
              <div className="mb-6 space-y-3">
                <div className="flex items-start">
                  <div className="flex items-center gap-3">
                    <Checkbox id="terms" />
                    <Label
                      htmlFor="terms"
                      className="text-gray-500 dark:text-gray-300"
                    >
                      By signing up, you are creating a Flowbite account, and
                      you agree to Flowbite’s&nbsp;
                      <a
                        className="font-medium text-primary-600 dark:text-primary-500 hover:underline"
                        href="#"
                      >
                        Terms of Use
                      </a>
                      &nbsp;and&nbsp;
                      <a
                        className="font-medium text-primary-600 dark:text-primary-500 hover:underline"
                        href="#"
                      >
                        Privacy Policy
                      </a>
                      .
                    </Label>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex items-center gap-3">
                    <Checkbox id="newsletter" />
                    <Label
                      htmlFor="newsletter"
                      className="text-gray-500 dark:text-gray-300"
                    >
                      Email me about product updates and resources.
                    </Label>
                  </div>
                </div>
              </div>
              <div className="flex flex-col space-y-3 md:flex-row md:space-x-3 md:space-y-0">
                <Button color="gray" href="#" className="md:w-1/2 hover:text-primary-600 hover:bg-gray-100 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700">
                  Prev: Personal Info
                </Button>
                <Button type="submit" className="md:w-1/2">
                  Next: Account Info
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AccountDetailsUserOnboarding;
