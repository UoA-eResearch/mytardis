import React, { useEffect, useState } from "react";
import { useCreateTransferMutation, useGetObjectByIdQuery, useGetRemoteHostsQuery, useGetSiteQuery, useValidateTransferQuery } from "../shared/api";
import PropTypes from "prop-types";
import { Accordion, Button, Card, Collapse, Form, FormControl, Modal } from "react-bootstrap";
import { Link, Redirect, Route, Switch, useHistory, useParams, useRouteMatch } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { addItemsTransferred, clearTransferredItems, getItemsByCategory, removeItem } from "./cartSlice";
import { BsCheck, BsChevronLeft, BsDashCircle, BsExclamationTriangle, BsExclamationTriangleFill, BsFillExclamationCircleFill, BsPlusCircle, BsTrash } from "react-icons/bs";
import { FiExternalLink } from "react-icons/fi";
import { CategoryTabs } from "../shared/CategoryTabs";
import { QueryStatus } from "@reduxjs/toolkit/dist/query";
import { Alert } from "react-bootstrap";
import { length } from "file-loader";
import humanFileSize from "../shared/humanFileSize";

// eslint-disable-next-line complexity
function CartItemRow({ typeId, id, canTransfer }) {
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
            <td>
                Error loading item.
            </td>
        </tr>;
    }
    const nameField = site.categories[typeId].name_field;
    const url = site.categories[typeId].details_uri + id;
    const name = item[nameField];
    return (<tr className={canTransfer ? null : "cart-item--invalid"}>
        <td className="category-item-list--remove">
            {canTransfer ? null : <BsExclamationTriangleFill title="This item can't be transferred because it belongs to a project or dataset that is not associated with the chosen transfer destination." />}
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
    id: PropTypes.string.isRequired,
    canTransfer: PropTypes.bool
};



export function CartCategoryTabs({selectedRemoteHost, selectedType, onChange}) {
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
function useSelectedCategoryState() {
    const [ selectedCategory, setSelectedCategory ] = useState();
    const {data: site, isLoading } = useGetSiteQuery({});

    useEffect(() => {
        // Set default category when our list of categories is loaded.
        // Make sure it's only done when categories loaded.
        if (site) {
            setSelectedCategory(Object.keys(site.categories)[0]);
        }
    }, [setSelectedCategory, site]);
    return [ selectedCategory, setSelectedCategory ];
}

function useGetHostInfoQuery(hostId) {
    return useGetRemoteHostsQuery(null, {
        selectFromResult: res => {
            if (res.status !== "fulfilled") {
                return res;
            }
            const data = res.data;
            const hostsById = Object.fromEntries(
                data.map(host => [host.id, host])
            );
            return Object.assign({}, res, {
                data: hostsById[hostId]
            });
        }
    });
}

function InvalidItemsWarning({ hostId }) {
    const [open, setOpen] = useState(false);
    const {data: hostInfo, isLoading } = useGetHostInfoQuery(hostId);
    const {data: invalidCount, isLoading: isValidationLoading } = useInvalidTransferItemsCount({remoteHostId: hostId});
    if (isLoading || isValidationLoading) {
        return <div className="my-3">
            <div className="spinner-border" role="status">
                <span className="sr-only">Loading...</span>
            </div>
        </div>;
    }
    if (invalidCount === 0 || !hostInfo) {
        return null;
    } 
    const remoteHostName = hostInfo.name;
    return <Alert variant="warning" className="mt-3">
        <BsExclamationTriangle className="mr-1" /> Some cart items can't be transferred to {remoteHostName}.
    </Alert>;
    // return <div className="d-flex">
    //         <div style={{fontSize: "2rem"}}>
                
    //         </div>
    //         <div className="pl-4">
    //             <h2 className="h5">Some cart items can't be transferred to {remoteHosts[selectedId].name}</h2>

    //         </div>
    //     </div>
    // </div>
    // return (
    //     <>
    //         <div className="invalid-items-warning my-2 py-2 px-3"
    //             role="button"
    //             aria-live="assertive"
    //             aria-controls="invalid-items-detail"
    //             aria-expanded={open}
    //             onClick={() => setOpen(!open)}>
    //             <span className="float-right">
    //                 {open ? <BsDashCircle /> : <BsPlusCircle />}
    //             </span>

    //             <span>
    //                 <BsExclamationTriangle fontSize="1.25rem" /> Some cart items can&apos;t be transferred to {remoteHostName}.
    //             </span>
    //         </div>
    //         <Collapse in={open}>
    //             <div id="invalid-items-detail" className="border border-top-0 px-3 py-3"> 
    //                 Some carts can&apos;t be transferred to the destination because they belong to a project or dataset not associated with the chosen destination. You can review the items that are ready for transfer and start a transfer, change your transfer endpoint, or go back to the cart to remove unwanted items.
    //             </div>
    //         </Collapse>
    //     </>
    // );
    // <Accordion>
    //     <Card className="mt-3">
    //         <Accordion.Toggle as={Card.Header} className="" eventKey="0">
    //             <BsExclamationTriangle /> Some cart items can&apos;t be transferred to {hostName}
    //         </Accordion.Toggle>
    //         <Accordion.Collapse eventKey="0">
    //             <Card.Body>
    //                 <p>
    //                     This is because they belong to a project or dataset not associated with this destination. You can review the items that are ready for transfer and start a transfer, change your transfer endpoint, or go back to the cart to remove unwanted items.
    //                 </p>
    //             </Card.Body>
    //         </Accordion.Collapse>
    //     </Card>
    // </Accordion>
    //     // <div className="alert alert-primary mt-3" role="alert">
    //     <BsExclamationTriangle /> Some cart items can't be transferred to {remoteHosts[selectedId].name}.
    // </div>
}

// eslint-disable-next-line complexity
function RemoteHostDropdown({selectedId, onSelect}) {
    const { data: remoteHosts, isLoading, error } = useGetRemoteHostsQuery();
    let output = null;
    if (isLoading) {
        output = <>
            <select className="form-control"
                aria-label="Transfer destination"
                size="lg"
                id="transfer-page--dropdown"
                disabled
            >
                <option key="notselected">Loading...</option>
            </select>
        </>;
    }
    else if (error) {
        output = <p>Error occurred while fetching list of Globus endpoints.</p>;
    } else {
        const remoteHostIds = remoteHosts.map(host => host.id);
        const hostsById = Object.fromEntries(
            remoteHosts.map(host => [host.id, host])
        );
        const selected = selectedId ? hostsById[selectedId].name : "";
        let remoteHostOptions;
        if (!remoteHosts || remoteHosts.length === 0) {
            remoteHostOptions = <option>No destinations available.</option>;
        } else {
            remoteHostOptions = remoteHosts.map(host => 
                <option key={host.id}>
                    {host.name}
                </option>);
            // Add a default, unselected option.
            remoteHostOptions.unshift(<option key="notselected">Select a destination</option>);
        }
        const handleSelected = (e) => {
            e.preventDefault();
            const selectedIndex = e.target.selectedIndex;
            if (selectedIndex === 0) {
                onSelect(null);
            } else {
                onSelect(remoteHostIds ? parseInt(remoteHostIds[selectedIndex - 1]) : null);
            }
        };
        output = <select className="form-control"
            aria-label="Transfer destination"
            size="lg"
            value={selected}
            id="transfer-page--dropdown"
            onChange={handleSelected}
        >
            {remoteHostOptions}
        </select>;
    }
    return <div className="transfer-screen--remotehost-list">
        {output}
    </div>;
}

RemoteHostDropdown.propTypes = {
    selectedId: PropTypes.string,
    onSelect: PropTypes.func.isRequired
};

function CategoryItemList({ children }) {
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
            {children}
        </tbody>
    </table>
    {children.length === 0 && 
        <div className="mt-5 d-flex justify-content-center" role="status">
            No items to be transferred.
        </div>
    }</>);
}

CategoryItemList.propTypes = {
    children: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.node),
        PropTypes.node
    ]).isRequired
};

const VALID_TRANSFER_FILTER_STATES = {
    All: "ALL",
    Invalid: "INVALID",
    Valid: "VALID"
};


function getItemsByState(items = [], invalidItems = [], validState) {
    // const invalidTypeItems = validationErrors.invalidItems ? validationErrors.invalidItems[type] : [];
    // const typeItems = items.byId[typeId];
    switch (validState) {
        case VALID_TRANSFER_FILTER_STATES.All:
            return items;
        case VALID_TRANSFER_FILTER_STATES.Invalid:
            return invalidItems;
        case VALID_TRANSFER_FILTER_STATES.Valid: {
            const invalidSet = new Set(invalidItems);
            return items.filter(item => !invalidSet.has(item));
        }
    }
}

function getInvalidItemsCount(invalidItems) {
    if (!invalidItems) {
        return 0;
    }
    return Object.keys(invalidItems).reduce(
        (acc, categoryId) => invalidItems[categoryId].length + acc, 0);

}


// eslint-disable-next-line complexity
export function TransferrableItemList({selectedRemoteHost}) {
    const {data: site, isLoading, error } = useGetSiteQuery({});
    const [ selectedCategory, setSelectedCategory ] = useSelectedCategoryState();
    const [ validFilterState, setValidFilterState ] = useState(VALID_TRANSFER_FILTER_STATES.All);
    const cartItems = useSelector(state => state.cart.itemsInCart.byId);
    const hasSelectedRemoteHost = selectedRemoteHost !== undefined && selectedRemoteHost !== null;
    const { data: validationErrors,
        isLoading: isValidationLoading,
        error: validationQueryError
    } = useValidateTransferQuery({
        remoteHostId: selectedRemoteHost,
        items: cartItems
    }, {
        skip: !hasSelectedRemoteHost,
        selectFromResult: (res) => {
            if (res.status === "fulfilled") {
                const data = res.data;
                if (hasSelectedRemoteHost && 
                    data &&
                    data.invalid_items) {
                    // Return the inner invalid_items object.
                    return Object.assign({}, res, {
                        data: data.invalid_items
                    });
                } else {
                    return Object.assign({}, res, {
                        data: {}
                    });
                }
            }
            // Return an empty object if not yet loaded.
            return Object.assign({}, res, {
                data: {}
            });
        }
    });
    const items = useSelector(state => state.cart.itemsInCart || {});
    let output = null;
    if (isLoading) {
        return <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
        </div>;
    }
    if (error) {
        return <p>Error loading items.</p>;
    }
    if (hasSelectedRemoteHost && validationQueryError) {
        console.log(validationQueryError.message);
        return <p>Error loading items.</p>;
    }
    const categories = Object.keys(site.categories);
    // Compute which items to display.
    const itemsToDisplay = Object.fromEntries(categories.map(categoryId =>
        [categoryId, getItemsByState(items.byId[categoryId], validationErrors[categoryId], validFilterState)]
    ));
    const tabItems = categories.map(categoryId =>
        ({
            name: site.categories[categoryId].collection_name,
            id: categoryId,
            hitTotal: itemsToDisplay[categoryId].length
        })
    );
    return <>
        <CategoryTabs counts={tabItems} selectedType={selectedCategory} onChange={setSelectedCategory} />
        {categories.map(categoryId => {
            const invalidItemSet = new Set(validationErrors[categoryId]);
            return <div className={selectedCategory !== categoryId ? "d-none category-item-list" : "category-item-list"} key={categoryId}>
                <CategoryItemList>
                    {itemsToDisplay[categoryId].map(item => (
                        <CartItemRow typeId={categoryId} id={item} canTransfer={!invalidItemSet.has(item)} key={categoryId + ":" + item} />
                    ))}
                </CategoryItemList>
            </div>;
        })}
    </>;
}
    // if (!validationErrors.invalidItems) {

    // }
    // const hostInfo = hosts[selectedRemoteHost];
    // const cantTransferItems = Object.keys(itemsInCart).map(typeId => {
    //     // Create a set for quicker lookup
    //     const transferrableItems = new Set(hostInfo.transferrableItems[typeId] || []);
    //     return itemsInCart[typeId].filter(itemId => !transferrableItems.has(itemId));
    // });
    // Object.keys(itemsInCart)

const TRANSFER_STATE = {
    Initial: "Initial",
    TransferRequested: "TransferRequested", // set to start a transfer
    NeedConfirmation: "NeedConfirmation", // has invalid items
    Confirmed: "Confirmed", // confirmed
    Transferring: "Transferring", // transferring
    Transferred: "Transferred" // transferred
};

function useInvalidTransferItemsCount({remoteHostId}) {
    const cartItems = useSelector(state => state.cart.itemsInCart.byId);
    return useValidateTransferQuery({
        remoteHostId,
        items: cartItems
    }, {skip: remoteHostId === undefined, selectFromResult: (res) => {
        if (res.status === "fulfilled") {
            const data = res.data;
            let count = 0;
            if (data) {
                count = getInvalidItemsCount(data.invalid_items);
            }
            // Replace the list of invalid items with the count.
            return Object.assign({}, res, {data: count});
        }
        return res;
    }});
}

function getValidItems(cartItems, invalidItems) {
    const validItems = {};
    Object.keys(cartItems).forEach(
        categoryId => {
            const invalidSet = new Set(invalidItems[categoryId]);
            validItems[categoryId] = cartItems[categoryId].filter(item => !invalidSet.has(item));
        }
    );
    return validItems;
}

function ConfirmTransferDialog({numInvalidItems, onConfirm, onCancel}) {
    return (
        <Modal show={true} onHide={onCancel}>
            <Modal.Header closeButton>
                <Modal.Title>Do you want to proceed with this transfer?</Modal.Title>
            </Modal.Header>
            <Modal.Body>{numInvalidItems} {numInvalidItems === 1 ? "item" : "items" } will not be included in the transfer because of restrictions on locations where these items can be transferred.</Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onCancel}>
                        Cancel
                </Button>
                <Button variant="primary" onClick={onConfirm}>
                        Yes, proceed
                </Button>
            </Modal.Footer>
        </Modal>
    );
}

ConfirmTransferDialog.propTypes = {
    numInvalidItems: PropTypes.number.isRequired,
    onConfirm: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired
};

// eslint-disable-next-line complexity
function CreateTransferDialog({remoteHostId, transferState, setTransferState}) {
    const cartItems = useSelector(state => state.cart.itemsInCart.byId);
    const [triggerTransfer, {status: transferMutationStatus}] = useCreateTransferMutation();
    const {data: invalidItems, isLoading: isValidationLoading, error: validationError } = useValidateTransferQuery({
        remoteHostId,
        items: cartItems
    });
    const numInvalidItems = invalidItems ? getInvalidItemsCount(invalidItems.invalid_items) : 0;
    let validItems = {};
    if (invalidItems) {
        validItems = getValidItems(cartItems, invalidItems.invalid_items);
    } 
    const dispatch = useDispatch();
    // const {data: numInvalidItems, isLoading: isValidationLoading} = useInvalidTransferItemsCount({remoteHostId});
    useEffect(() => {
        if (transferState !== TRANSFER_STATE.TransferRequested || isValidationLoading || validationError) {
            // If validation is still being loaded, wait until it's
            // loaded.
            return;
        }
        
        if (!numInvalidItems) {
            setTransferState(TRANSFER_STATE.Confirmed);
        } else {
            setTransferState(TRANSFER_STATE.NeedConfirmation);
        }

    }, [transferState, invalidItems, numInvalidItems, validationError, isValidationLoading]);

    useEffect(() => {
        if (transferState === TRANSFER_STATE.Confirmed) {
            triggerTransfer({remoteHostId, items: validItems});
            setTransferState(TRANSFER_STATE.Transferring);
        }
    }, [transferState]);
    useEffect(() => {
        if (transferMutationStatus === QueryStatus.fulfilled) {
            setTransferState(TRANSFER_STATE.Transferred);
        }
    }, [transferMutationStatus]);
    if (transferState === TRANSFER_STATE.NeedConfirmation) {
        return (
            <ConfirmTransferDialog numInvalidItems={numInvalidItems}
                onConfirm={() => setTransferState(TRANSFER_STATE.Confirmed)}
                onCancel={() => setTransferState(TRANSFER_STATE.Initial)}
            />
        );
    }
    if (transferState === TRANSFER_STATE.Confirmed) {
        return <p>Sending...</p>;
    }
    if (transferState === TRANSFER_STATE.Transferred) {
        dispatch(addItemsTransferred(validItems));
        return <Redirect to="/transfer/done" />;
    }
    else { 
        return null;
    }
}

function TransferScreen(props) {
    const [selectedRemoteHost, setSelectedRemoteHost] = useState();
    const history = useHistory();
    const goToConfirmScreen = () => {
        history.push(`/transfer/${selectedRemoteHost}`);
    };
    return <div>
        <div className="mb-3">
            <Link to="/"><BsChevronLeft />Go back</Link>
        </div>
        <h1 className="mb-2 h4 text-secondary font-weight-light">Transfer to a Globus endpoint</h1>
        <h2 className="mb-3 h1">Select a transfer destination</h2>
        <p className="text-secondary">Can't see your Globus endpoint? Contact your data repository support team to add it to MyTardis.</p>
        <RemoteHostDropdown selectedId={selectedRemoteHost} onSelect={setSelectedRemoteHost} />
        <div className="d-flex justify-content-between mt-5">
            <button 
                className="btn btn-primary"
                disabled={!selectedRemoteHost}
                aria-disabled={!selectedRemoteHost}
                onClick={goToConfirmScreen}
            >
                Continue
            </button>
        </div>

    </div>;
}

// function Transfer

function TransferConfirmScreen() {
    const { hostId } = useParams();
    const [transferState, setTransfer] = useState(TRANSFER_STATE.Initial);
    const { data: hostInfo, isLoading: isLoadingHostInfo } = useGetHostInfoQuery(hostId);
    const {data: invalidCount, isLoading: isValidationLoading} = useInvalidTransferItemsCount({remoteHostId: hostId});
    return (<>
        <div className="mb-3">
            <Link to="/transfer"><BsChevronLeft />Go back</Link>
        </div>
        <h1 className="mb-2 h4 text-secondary font-weight-light">Transfer to a Globus endpoint</h1>
        <h2 className="mb-3 h1">Review items to be transferred</h2>
        <p className="text-secondary">To change, go back to the cart to add or remove items.</p>
        <InvalidItemsWarning hostId={hostId} />
        <TransferrableItemList selectedRemoteHost={hostId} />
        <section className="my-4">
            <dl className="d-flex border-bottom">
                <dt className="col-md-8">
                    Transfer destination
                </dt>
                <dd className="col-md-2">
                    {hostInfo ? hostInfo.name : null}
                </dd>
                <dd className="col-md-2 text-right">
                    <Link to="/transfer">Change</Link>
                </dd>
            </dl>
        </section>
        <div className="mt-4">
            <button 
                className="btn btn-primary"
                onClick={() => setTransfer(TRANSFER_STATE.TransferRequested)}
            >
                Start transfer
            </button>
        </div>
        <CreateTransferDialog 
            remoteHostId={hostId} 
            transferState={transferState} 
            setTransferState={setTransfer} 
        />
    </>);
}

function TransferCompletedScreen() {
    const dispatch = useDispatch();
    const history = useHistory();
    const transferredItems = useSelector(state => state.cart.transferredItems);
    const [shouldRemoveTransferred, setShouldRemoveTransferred] = useState(true);
    const numTransferred = Object.keys(transferredItems).reduce(
        (acc, typeId) => acc + transferredItems[typeId].length, 0);
    const toggleShouldRemoveTransferred = () => {
        setShouldRemoveTransferred(!shouldRemoveTransferred);
    };
    const handleVisitCart = () => {
        dispatch(clearTransferredItems(shouldRemoveTransferred));
        history.replace("/");
    };

    if (numTransferred === 0) {
        // If there aren't any transferred items, go back to the cart.
        const redirectPath = "/";
        return <Redirect to={redirectPath} />;
    }
    
    return <>
        <h1 className="mb-2 h4 text-secondary font-weight-light">Transfer to a Globus endpoint</h1>
        <h2 className="h1 mb-3">Transfer started</h2>
        <p><strong>{numTransferred} {numTransferred === 1 ? "item" : "items"} have started transferring.</strong></p>
        <p>Depending on the size of the items it may take several hours for the items to finish transferring to the destination. You can check progress of the transfer through the Transfers page (todo).</p>
        <Form.Check 
            type="checkbox" 
            checked={shouldRemoveTransferred}
            onChange={toggleShouldRemoveTransferred}
            id="shouldTransfer"
            label="Remove transferred items from cart" 
        />
        <div className="d-flex justify-content-between mt-4">
            <Button role="link" onClick={handleVisitCart} className="btn btn-primary" to="/cart">Go back to cart</Button>
        </div>
    </>;
}

function TransferRoute(props) {
    const match = useRouteMatch();
    return <Switch>
        <Route path={`${match.path}/done`}>
            <TransferCompletedScreen />
        </Route>
        <Route path={`${match.path}/:hostId`}>
            <TransferConfirmScreen />
        </Route>
        <Route path={`${match.path}`}>
            <TransferScreen />
        </Route>
    </Switch>;
}

export default TransferRoute;