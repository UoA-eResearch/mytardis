import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import { BsTrash } from "react-icons/bs";
import { FiExternalLink } from "react-icons/fi";
// import Button from "react-bootstrap/Button";
import { CategoryTabs } from "../shared/CategoryTabs";
// import { getCategoriesAsList, getDefaultSelectedCategory } from "../shared/siteSlice";
import { useGetObjectByIdQuery, useGetSiteQuery } from "../shared/api";
import { getItemsByCategory, removeItem } from "./cartSlice";
import humanFileSize from "../shared/humanFileSize";

function CartItemRow({ typeId, id }) {
    const dispatch = useDispatch();
    const { data: site, isLoading: isSiteLoading } = useGetSiteQuery();
    const endpointName = site ? site.categories[typeId].endpoint_name : null;
    const { isLoading: isObjectLoading, data: item } = useGetObjectByIdQuery({
        name: endpointName,
        id
    }, {
        // Wait for site query to finish loading.
        skip: isSiteLoading
    });
    if (isSiteLoading || isObjectLoading) {
        return <tr></tr>;
    }

    if (!item) {
        return <tr>
            <td rowSpan="3">
                Not found!
            </td>
        </tr>;
    }
    const nameField = site.categories[typeId].name_field;
    const url = site.categories[typeId].details_uri + id;
    const name = item[nameField];
    const handleRemoveClicked = (e) => {
        e.preventDefault();
        dispatch(removeItem(typeId, id));
    };
    return (<tr>
        <td className="category-item-list--remove">
            <button onClick={handleRemoveClicked} className="btn btn-light"><BsTrash /></button>
        </td>
        <td className="category-item-list--name">
            {/* Name cell */}
            <a href={url} target="_blank" rel="noopener noreferrer">{name} <FiExternalLink /></a> 
        </td>
        <td className="category-item-list--size">
            <span>{humanFileSize(item.size)}</span>
        </td>
    </tr>);
}

CartItemRow.propTypes = {
    typeId: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired
};


function CategoryItemList({ typeId }) {
    const categoryItems = useSelector(
        state => 
            getItemsByCategory(state.cart, typeId));

    return (<>
    <table className="table">
        <thead>
            <tr>
                <th></th>
                <th>Name</th>
                <th>Size</th>
            </tr>
        </thead>
        <tbody>
            {categoryItems.map(itemId => 
                <CartItemRow typeId={typeId} id={itemId} key={itemId} />
            )}
        </tbody>
    </table>
    {categoryItems.length === 0 && 
        <div className="mt-5 d-flex justify-content-center" role="status">
            No items in cart.
        </div>
    }</>);
}

CategoryItemList.propTypes = {
    typeId: PropTypes.string.isRequired
};

export function CartCategoryTabs({selectedType, onChange}) {
    const {data: site} = useGetSiteQuery({});
    const counts = useSelector(state => {
        if (!site) {
            return null;
        }
        const categories = site.categories;
        const categoryKeys = Object.keys(categories);
        return categoryKeys.map(key => {
            const categoryItemsInCart = state.cart.itemsInCart.byId[key] || [];
            return {
                name: site.categories[key].collection_name,
                id: key,
                hitTotal: categoryItemsInCart.length
            };
        });
    });
    if (!counts) {
        return null;
    } else {
        return (<CategoryTabs counts={counts} selectedType={selectedType} onChange={onChange} />);
    }
}

/**
 * Create a React hook for storing the currently selected category. 
 * Get query API, in order to provide a default category.
 * @returns A state variable for a category key, and a callback for changing it.
 */
function useSelectedCategoryState(site) {
    const [ selectedCategory, setSelectedCategory ] = useState();

    useEffect(() => {
        // Set default category when our list of categories is loaded.
        // Make sure it's only done when categories loaded.
        if (site) {
            setSelectedCategory(Object.keys(site.categories)[0]);
        }
    }, [setSelectedCategory, site]);
    return [ selectedCategory, setSelectedCategory ];
}


export default function CartItemList() {
    const {data: site, isLoading } = useGetSiteQuery({});
    const [ selectedCategory, setSelectedCategory ] = useSelectedCategoryState(site);
    if (isLoading) {
        return <p>Loading...</p>;
    }
    if (!site) {
        return <p>Error loading cart.</p>;
    }
    const categories = Object.keys(site.categories);

    return (
        <div>
            <CartCategoryTabs selectedType={selectedCategory} onChange={setSelectedCategory} />
            {categories.map(categoryId => (
                <div className={selectedCategory !== categoryId ? "d-none category-item-list" : "category-item-list"} key={categoryId}>
                    <CategoryItemList typeId={categoryId} />    
                </div>
            ))}
        </div>
    );
}