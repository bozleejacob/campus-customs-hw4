# Usability Improvements

## Front-end

1. **Auto-scroll the chat panel to the newest message.** Shoppers no longer have to manually scroll down after every reply to see what the assistant just said, which keeps the conversation feeling responsive instead of broken.
2. **Cross-links between the Login and Create Account pages.** A shopper who lands on the wrong form can switch in one click instead of hunting for the right nav link, removing a small but real drop-off point right before signup/login.

## Agent backend

1. **Suggest in-stock alternatives when an item or size is unavailable.** Instead of ending the conversation on "that's out of stock," the agent now searches for and offers similar in-stock items, turning a dead end into a second chance at a sale.
2. **One automatic retry on a failed agent/model call before apologizing.** Transient hiccups (a flaky model response, a brief provider error) get a silent second attempt first, so shoppers see a real answer instead of an unnecessary "something went wrong" more often than they otherwise would.
