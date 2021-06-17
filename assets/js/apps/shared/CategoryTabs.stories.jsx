import React from "react";
import { CategoryTabs } from "./CategoryTabs";

export default {
    component: CategoryTabs,
    title: "Shared/Category tabs",
    decorators: [story => <div style={{ padding: "3rem" }}>{story()}</div>],
    parameters: { actions: { argTypesRegex: "^on.*" } }
};

const Template = (args) => <CategoryTabs {...args} />;

export const Default = Template.bind({});
Default.args = {
    counts: [
        {
            name: "Projects",
            id: "project",
            hitTotal: 4
        },
        {
            name: "Experiments",
            id: "experiment",
            hitTotal: 10
        },
        {
            name: "Datasets",
            id: "dataset",
            hitTotal: 33
        },
        {
            name: "Datafiles",
            id: "datafile",
            hitTotal: 405
        },
    ],
    selectedType: "project"
};

export const NoProjects = Template.bind({});
NoProjects.args = Object.assign(Default, {
    selectedType: "experiment",
    counts: Default.args.counts.filter(c => c.id !== "project")
});

export const EmptyCounts = Template.bind({});
EmptyCounts.args = {
    counts: [
        {
            id: "project",
            name: "projects"
        },
        {
            id: "experiment",
            name: "experiments"
        },
        {
            id: "dataset",
            name: "datasets"
        },
        {
            id: "datafile",
            name: "datafiles"
        }
    ],
    selectedType: "experiment"
};