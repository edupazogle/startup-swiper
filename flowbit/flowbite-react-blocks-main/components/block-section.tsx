import { Button } from "flowbite-react";
import type { FC, PropsWithChildren } from "react";
import { FaGithub } from "react-icons/fa";

export interface BlockSectionProps extends PropsWithChildren {
  description: string;
  githubLink: string;
  title: string;
}

const BlockSection: FC<BlockSectionProps> = function ({
  children,
  description,
  githubLink,
  title,
}) {
  return (
    <section className="mb-12 max-w-screen-2xl mx-auto px-4">
      <div className="mb-6 pb-4 flex flex-col gap-3 md:flex-row items-center md:justify-between md:space-x-4">
        <div>
          <header>
            <h2 className="mb-1 text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
              {title}
            </h2>
          </header>
          <p className="text-lg text-gray-500 dark:text-gray-400 lg:mb-0 max-w-2xl">
            {description}
          </p>
        </div>
        <Button href={githubLink} target="_blank" className="dark:hover:bg-gray-700 w-full md:w-auto flex-shrink-0 ml-0 hover:bg-gray-50 hover:text-primary-600 dark:hover:text-white" color="gray">
          <FaGithub className="mr-3 h-5 w-5" />
          View on GitHub
        </Button>
      </div>
      <div className="w-full border border-gray-100 dark:border-gray-800 rounded-lg">{children}</div>
    </section>
  );
};

export default BlockSection;
