import { Button, Label, TextInput, Textarea } from "flowbite-react";
import type { FC } from "react";

const DefaultContactForm: FC = function () {
  return (
    <section className="bg-white dark:bg-gray-900">
      <div className="mx-auto max-w-screen-md px-4 py-8 lg:py-16">
        <h2 className="mb-4 text-center text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white">
          Contact Us
        </h2>
        <p className="mb-8 text-center text-gray-500 dark:text-gray-400 sm:text-xl lg:mb-16">
          Got a technical issue? Want to send feedback about a beta feature?
          Need details about our Business plan? Let us know.
        </p>
        <form action="#" className="space-y-8">
          <div className="grid grid-cols-1 gap-2">
            <Label htmlFor="email" className="dark:text-white">Your email</Label>
            <TextInput
              id="email"
              placeholder="name@flowbite.com"
              required
              type="email"
            />
          </div>
          <div className="grid grid-cols-1 gap-2">
            <Label htmlFor="subject" className="dark:text-white">Subject</Label>
            <TextInput
              id="subject"
              placeholder="Let us know how we can help you"
              required
              type="text"
            />
          </div>
          <div className="grid grid-cols-1 gap-2 sm:col-span-2">
            <Label htmlFor="message" className="dark:text-white">Your message</Label>
            <Textarea id="message" placeholder="Leave a comment..." className="text-sm" rows={6} />
          </div>
          <Button type="submit">Send message</Button>
        </form>
      </div>
    </section>
  );
};

export default DefaultContactForm;
