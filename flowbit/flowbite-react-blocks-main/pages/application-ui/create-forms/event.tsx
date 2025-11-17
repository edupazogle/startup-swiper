import {
  Avatar,
  Button,
  Checkbox,
  Datepicker,
  Label,
  Select,
  TextInput,
  Textarea,
  Tooltip,
} from "flowbite-react";
import type { FC } from "react";

const CreateEventForm: FC = function () {
  return (
    <section className="bg-white dark:bg-gray-900">
      <div className="py-8 px-4 mx-auto md:max-w-6xl lg:py-16">
        <h2 className="mb-4 text-xl font-bold text-gray-900 dark:text-white">
          Add a new event
        </h2>
        <form>
          <div className="gap-4 sm:grid sm:grid-cols-2 xl:grid-cols-3 sm:gap-6 sm:mb-2">
            <div className="mb-4 space-y-4 xl:col-span-2">
              <div>
                <Label htmlFor="title" className="block mb-2 dark:text-white">
                  Title
                </Label>
                <TextInput
                  id="title"
                  name="title"
                  placeholder="Add title here"
                  required
                />
              </div>
              <div>
                <Label
                  htmlFor="date_start"
                  className="block mb-2 dark:text-white"
                >
                  Select Date
                </Label>
                <div className="items-center space-y-4 md:flex md:space-y-0">
                  <div className="relative w-full">
                    <div className="flex absolute inset-y-0 left-0 items-center pl-3 pointer-events-none">
                      <svg
                        aria-hidden
                        className="w-5 h-5 text-gray-500 dark:text-gray-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          fillRule="evenodd"
                          d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <Datepicker
                      id="date_start"
                      name="start"
                      value="Select date start"
                      className="[&_input]:dark:text-gray-400"
                    />
                  </div>
                  <span className="hidden text-gray-500 md:mx-4 md:flex">
                    to
                  </span>
                  <div className="relative w-full">
                    <div className="flex absolute inset-y-0 left-0 items-center pl-3 pointer-events-none">
                      <svg
                        aria-hidden
                        className="w-5 h-5 text-gray-500 dark:text-gray-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          fillRule="evenodd"
                          d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <Datepicker
                      id="date_end"
                      name="end"
                      value="Select date end"
                      className="[&_input]:dark:text-gray-400"
                    />
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex items-center w-20">
                  <Checkbox id="event-duration-checkbox" />
                  <Label
                    htmlFor="event-duration-checkbox"
                    className="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
                  >
                    All day
                  </Label>
                </div>
                <Label htmlFor="time" className="sr-only">
                  Select an option
                </Label>
                <Select id="time">
                  <option selected>Does not repeat</option>
                  <option value="DA">Daily</option>
                  <option value="WW">Weekly on Wednesday</option>
                  <option value="EW">Every weekday</option>
                  <option value="CU">Custom</option>
                </Select>
              </div>
              <button className="text-white bg-[#4285F4] hover:bg-[#4285F4]/90 focus:ring-4 focus:outline-none focus:ring-[#4285F4]/50 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-[#4285F4]/55 mr-2 mb-2">
                <svg
                  aria-hidden
                  focusable="false"
                  data-prefix="fab"
                  data-icon="google"
                  role="img"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 488 512"
                  className="mr-2 -ml-1 w-4 h-4"
                >
                  <path
                    fill="currentColor"
                    d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"
                  />
                </svg>
                Add Google Meet video conference
              </button>
              <div>
                <div className="block mb-2 dark:text-white">Tag Color</div>
                <div className="flex items-center space-x-2">
                  <button className="w-6 h-6 bg-purple-500 rounded-sm" />
                  <button className="w-6 h-6 bg-indigo-500 rounded-sm" />
                  <button className="w-6 h-6 rounded-sm bg-primary-600" />
                  <button className="w-6 h-6 bg-pink-500 rounded-sm" />
                  <button className="w-6 h-6 bg-teal-400 rounded-sm" />
                  <button className="w-6 h-6 bg-green-400 rounded-sm" />
                  <button className="w-6 h-6 bg-yellow-300 rounded-sm" />
                  <button className="w-6 h-6 bg-orange-400 rounded-sm" />
                  <button className="w-6 h-6 bg-red-500 rounded-sm" />
                </div>
              </div>
              <div>
                <Label
                  htmlFor="description"
                  className="block mb-2 dark:text-white"
                >
                  Description
                </Label>
                <div className="mb-4 w-full bg-gray-100 rounded-lg border border-gray-200 dark:bg-gray-600 dark:border-gray-600">
                  <div className="flex justify-between items-center py-2 px-3 border-b dark:border-gray-600">
                    <div className="flex flex-wrap items-center divide-gray-200 sm:divide-x dark:divide-gray-600">
                      <div className="flex items-center space-x-1 sm:pr-4">
                        <button className="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600">
                          <svg
                            aria-hidden
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-5 h-5"
                          >
                            <path
                              fillRule="evenodd"
                              d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="sr-only">Attach file</span>
                        </button>
                        <button className="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600">
                          <svg
                            aria-hidden
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-5 h-5"
                          >
                            <path
                              fillRule="evenodd"
                              d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="sr-only">Embed map</span>
                        </button>
                        <button className="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600">
                          <svg
                            aria-hidden
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-5 h-5"
                          >
                            <path
                              fillRule="evenodd"
                              d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="sr-only">Upload image</span>
                        </button>
                        <button className="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600">
                          <svg
                            aria-hidden
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-5 h-5"
                          >
                            <path
                              fillRule="evenodd"
                              d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="sr-only">Format code</span>
                        </button>
                        <button className="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600">
                          <svg
                            aria-hidden
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-5 h-5"
                          >
                            <path
                              fillRule="evenodd"
                              d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zm-.464 5.535a1 1 0 10-1.415-1.414 3 3 0 01-4.242 0 1 1 0 00-1.415 1.414 5 5 0 007.072 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="sr-only">Add emoji</span>
                        </button>
                      </div>
                      <div className="hidden flex-wrap items-center space-x-1 sm:flex sm:pl-4">
                        <button className="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600">
                          <svg
                            aria-hidden
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-5 h-5"
                          >
                            <path
                              fillRule="evenodd"
                              d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="sr-only">Timeline</span>
                        </button>
                        <button className="p-2 text-gray-500 rounded cursor-pointer hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600">
                          <svg
                            aria-hidden
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                            className="w-5 h-5"
                          >
                            <path
                              fillRule="evenodd"
                              d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <span className="sr-only">Download</span>
                        </button>
                      </div>
                    </div>
                    <Tooltip content="Show full screen">
                      <button className="p-2 text-gray-500 rounded cursor-pointer sm:ml-auto hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-600">
                        <svg
                          aria-hidden
                          fill="currentColor"
                          viewBox="0 0 20 20"
                          xmlns="http://www.w3.org/2000/svg"
                          className="w-5 h-5"
                        >
                          <path
                            fillRule="evenodd"
                            d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z"
                            clipRule="evenodd"
                          />
                        </svg>
                        <span className="sr-only">Full screen</span>
                      </button>
                    </Tooltip>
                  </div>
                  <div className="py-2 px-4 bg-gray-50 rounded-b-lg dark:bg-gray-700">
                    <Textarea
                      id="description"
                      name="description"
                      placeholder="Write a description here"
                      required
                      rows={8}
                      className="px-0 text-sm border-0 focus:ring-0"
                    />
                  </div>
                </div>
              </div>
              <div>
                <div className="block mb-2 dark:text-white">Reminder</div>
                <div className="space-y-4 md:flex md:space-y-0 md:space-x-4">
                  <div className="w-full">
                    <Label htmlFor="reminder-type" className="sr-only">
                      Reminder type
                    </Label>
                    <Select id="reminder-type">
                      <option selected>Notification</option>
                      <option value="AL">Alarm</option>
                      <option value="EM">Email</option>
                      <option value="SM">SMS</option>
                    </Select>
                  </div>
                  <div className="w-full">
                    <Label htmlFor="reminder-counter" className="sr-only">
                      Counter
                    </Label>
                    <TextInput
                      id="reminder-counter-days"
                      name="reminder-counter"
                      placeholder="1"
                      required
                      type="number"
                    />
                  </div>
                  <div className="w-full">
                    <Label htmlFor="reminder-length-type" className="sr-only">
                      Length
                    </Label>
                    <Select id="reminder-length-type">
                      <option selected>Days</option>
                      <option value="WE">Weeks</option>
                      <option value="MO">Months</option>
                    </Select>
                  </div>
                </div>
              </div>
            </div>
            <div className="mb-4 space-y-4">
              <div>
                <Label
                  htmlFor="add-guests"
                  className="block mb-2 dark:text-white"
                >
                  Add guests
                </Label>
                <div className="relative">
                  <TextInput
                    id="add-guests"
                    placeholder="Add guest email"
                    required
                  />
                  <Button className="[&>span]:p-0 [&>span]:text-xs text-white absolute inline-flex items-center right-2.5 bottom-2.5 top-1.5 bg-primary-700 hover:bg-primary-800 focus:ring-4 focus:outline-none focus:ring-primary-300 font-medium rounded-lg px-3 py-1.5 dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800">
                    <svg
                      className="w-4 h-4 -ml-0.5 mr-0.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Add
                  </Button>
                </div>
              </div>
              <div className="items-center md:flex md:space-x-4">
                <Avatar.Group className="flex-shrink-0 flex mb-4 md:mb-0 [&_img]:h-8 [&_img]:w-8 dark:[&_img]:ring-gray-800 [&_img]:ring-white">
                  <Avatar
                    alt="Helene Engels"
                    img="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/helene-engels.png"
                    stacked
                    rounded
                    className="ring-white"
                  />
                  <Avatar
                    alt="Robert Brown"
                    img="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/robert-brown.png"
                    stacked
                    rounded
                  />
                  <Avatar
                    alt="Bonnie Green"
                    img="https://flowbite.s3.amazonaws.com/blocks/marketing-ui/avatars/bonnie-green.png"
                    stacked
                    rounded
                    className="ring-white"
                  />
                  <Avatar.Counter
                    href="#"
                    total={9}
                    className="h-8 w-8 dark:ring-gray-800 ring-white"
                  />
                </Avatar.Group>
                <Button
                  color="gray"
                  outline
                  className="inline-flex [&>span]:text-xs [&>span]:text-gray-900 [&>span]:bg-white [&>span]:border-gray-200 focus:outline-none hover:bg-gray-100 hover:text-primary-700 focus:ring-gray-100 dark:focus:ring-gray-700 dark:[&>span]:bg-gray-800 dark:[&>span]:text-gray-400 dark:[&>span]:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
                >
                  <svg
                    aria-hidden
                    className="mr-1 -ml-1 w-4 h-4"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Add member
                </Button>
                <Button
                  color="gray"
                  outline
                  className="inline-flex [&>span]:text-xs [&>span]:text-gray-900 [&>span]:bg-white [&>span]:border-gray-200 focus:outline-none hover:bg-gray-100 hover:text-primary-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:[&>span]:bg-gray-800 dark:[&>span]:text-gray-400 dark:[&>span]:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
                >
                  <svg
                    aria-hidden
                    className="mr-1 -ml-1 w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Find a time
                </Button>
              </div>
              <div>
                <p className="block mb-2 dark:text-white">Guest Permissions</p>
                <div className="space-y-3">
                  <div className="flex items-center mr-4">
                    <Checkbox
                      id="guest-permission-1-checkbox"
                      name="guest-permission-checkbox"
                    />
                    <Label
                      htmlFor="guest-permission-1-checkbox"
                      className="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
                    >
                      Modify event
                    </Label>
                  </div>
                  <div className="flex items-center mr-4">
                    <Checkbox
                      id="guest-permission-2-checkbox"
                      name="guest-permission-checkbox"
                    />
                    <Label
                      htmlFor="guest-permission-2-checkbox"
                      className="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
                    >
                      Invite others
                    </Label>
                  </div>
                  <div className="flex items-center mr-4">
                    <Checkbox
                      checked
                      id="guest-permission-3-checkbox"
                      name="guest-permission-checkbox"
                    />
                    <Label
                      htmlFor="guest-permission-3-checkbox"
                      className="ml-2 text-sm font-medium text-gray-900 dark:text-gray-300"
                    >
                      See guest list
                    </Label>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <Button type="submit">Add new event</Button>
        </form>
      </div>
    </section>
  );
};

export default CreateEventForm;
