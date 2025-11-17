import { Button, Datepicker, Label, Select, TextInput } from "flowbite-react";
import type { FC } from "react";

const SearchBarDatepickerHeroSection: FC = function () {
  return (
    <section className="bg-[url('https://flowbite.s3.amazonaws.com/blocks/marketing-ui/hero/coast-house-view.jpg')] bg-no-repeat bg-cover bg-center bg-gray-700 bg-blend-multiply">
      <div className="relative py-8 px-4 mx-auto max-w-screen-xl text-white lg:py-16 xl:px-0 z-1">
        <div className="mb-6 max-w-screen-md lg:mb-0">
          <h1 className="mb-4 text-4xl font-extrabold tracking-tight leading-tight text-white md:text-5xl lg:text-6xl">
            Every home is a destination
          </h1>
          <p className="mb-6 text-gray-300 lg:mb-8 md:text-lg lg:text-xl">
            The best of Luxury Retreats is now Flowbite Luxe—offering the
            world's most extraordinary homes with the highest standard of
            service.
          </p>
          <a
            href="#"
            className="inline-flex items-center py-3 px-5 font-medium text-center text-white rounded-lg bg-primary-700 hover:bg-primary-800 focus:ring-4 focus:outline-none focus:ring-primary-900 dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800"
          >
            Sign In / Register
          </a>
        </div>
        <form
          action="#"
          className="grid gap-y-4 p-4 mt-8 w-full bg-white rounded lg:gap-x-4 lg:grid-cols-9 lg:mt-12 dark:bg-gray-800"
        >
          <div className="lg:col-span-3">
            <Label htmlFor="location-form" className="sr-only">
              Location
            </Label>
            <TextInput id="location-form" placeholder="Search destinations" />
          </div>
          <div className="grid grid-cols-2 gap-x-4 lg:col-span-3">
            <Datepicker value="Check in" />
            <Datepicker value="Check out" />
          </div>
          <div className="lg:col-span-1">
            <Label htmlFor="guests" className="sr-only">
              Select number of guests
            </Label>
            <Select id="guests">
              <option>Add guests</option>
              <option>1</option>
              <option>2</option>
              <option>3</option>
              <option>4</option>
              <option>5+</option>
            </Select>
          </div>
          <Button type="submit" className="lg:col-span-2">
            <svg
              className="mr-2 -ml-1 w-5 h-5"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                clipRule="evenodd"
              />
            </svg>
            Search
          </Button>
        </form>
      </div>
    </section>
  );
};

export default SearchBarDatepickerHeroSection;
