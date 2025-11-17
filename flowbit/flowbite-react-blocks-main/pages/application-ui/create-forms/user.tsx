import { Button, Label, TextInput, Textarea } from "flowbite-react";
import type { FC } from "react";

const CreateUserForm: FC = function () {
  return (
    <section className="bg-white dark:bg-gray-900">
      <div className="py-8 px-4 mx-auto max-w-2xl lg:py-16">
        <h2 className="mb-4 text-xl font-bold text-gray-900 dark:text-white">
          Add a new user
        </h2>
        <form>
          <div className="grid gap-4 sm:grid-cols-2 sm:gap-6">
            <div>
              <Label
                htmlFor="first-name"
                className="block mb-2 dark:text-white"
              >
                First Name
              </Label>
              <TextInput
                id="first-name"
                name="first-name"
                placeholder="First name"
                required
              />
            </div>
            <div className="w-full">
              <Label htmlFor="last-name" className="block mb-2 dark:text-white">
                Last Name
              </Label>
              <TextInput
                id="last-name"
                name="last-name"
                placeholder="Last name"
                required
              />
            </div>
            <div>
              <Label htmlFor="password" className="block mb-2 dark:text-white">
                Password
              </Label>
              <TextInput
                id="password"
                name="password"
                placeholder="•••••••••"
                required
                type="password"
              />
            </div>
            <div>
              <Label
                htmlFor="confirm-password"
                className="block mb-2 dark:text-white"
              >
                Confirm password
              </Label>
              <TextInput
                id="confirm-password"
                name="confirm-password"
                placeholder="•••••••••"
                required
                type="password"
              />
            </div>
            <div className="sm:col-span-2">
              <Label htmlFor="biography" className="block mb-2 dark:text-white">
                Biography
              </Label>
              <Textarea
                id="biography"
                placeholder="Your description here"
                rows={8}
                className="text-sm"
              />
            </div>
          </div>
          <Button type="submit" className="mt-6">
            Add user
          </Button>
        </form>
      </div>
    </section>
  );
};

export default CreateUserForm;
