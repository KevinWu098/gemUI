import * as React from 'react'

import { shareChat } from '@/app/actions'
import { Button } from '@/components/ui/button'
import { PromptForm } from '@/components/prompt-form'
import { ButtonScrollToBottom } from '@/components/button-scroll-to-bottom'
import { IconShare } from '@/components/ui/icons'
import { FooterText } from '@/components/footer'
import { ChatShareDialog } from '@/components/chat-share-dialog'
import { useAIState, useActions, useUIState } from 'ai/rsc'
import type { AI } from '@/lib/chat/actions'
import { nanoid } from 'nanoid'
import { BotThought, BotUI, UserMessage } from './stocks/message'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

import parse from 'html-react-parser'

export interface ChatPanelProps {
  id?: string
  title?: string
  input: string
  setInput: (value: string) => void
  isAtBottom: boolean
  scrollToBottom: () => void
}

export interface ServerMessage {
  event: 'thought' | 'ui'
  data:
    | {
        thought: string
      }
    | { html: string }
    | Object
}

const exampleMessages = [
  {
    heading: 'Order a Pepperoni Pizza online',
    subheading: "from Domino's Pizza",
    message: "Order me a Pepperoni Pizza online from Domino's Pizza"
  },
  {
    heading: 'Check your medical coverage',
    subheading: "on Kaiser Permanente's dashboard",
    message: `Check my medical coverage on Kaiser Permanente's dashboard`
  }
]

const SocketIndicator = ({ socket }: { socket: WebSocket | undefined }) => {
  const state = socket?.readyState
  console.log(state)

  return (
    <div
      className={cn(
        'fixed bottom-1 right-1 z-50 size-6 rounded-full bg-gray-800 p-3',
        !state || state === socket?.CLOSED
          ? 'bg-red-500'
          : state === socket?.CLOSING
            ? 'bg-yellow-500'
            : state === socket?.OPEN
              ? 'bg-green-500'
              : 'bg-red-500'
        // state === socket?.CLOSING && 'bg-yellow-500',
        // state === socket?.OPEN && 'bg-green-500'
      )}
    />
  )
}

export function ChatPanel({
  id,
  title,
  input,
  setInput,
  isAtBottom,
  scrollToBottom
}: ChatPanelProps) {
  const [aiState] = useAIState()
  const [messages, setMessages] = useUIState<typeof AI>()
  // const { submitUserMessage } = useActions()
  const [shareDialogOpen, setShareDialogOpen] = React.useState(false)

  const [socket, setSocket] = React.useState<WebSocket>()

  React.useEffect(() => {
    setSocket(new WebSocket('ws://localhost:8000/ws?client_id=123'))
  }, [])

  const submitUserMessage = (message: string) => {
    // getDummyResponse()

    if (!socket) {
      console.log('Socket not connected')
      return
    }

    socket.send(JSON.stringify({ event: 'prompt', prompt: message }))
    console.log('Message Sent')
  }

  const containerRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    const handleClick = (event: any) => {
      const id = event.target.getAttribute('id')
      console.log(id)
    }

    if (!containerRef.current) {
      return
    }

    const clickables = containerRef.current.querySelectorAll('div[id]')
    // console.log(containerRef.current, clickables)

    clickables.forEach((clickable: Element) => {
      clickable.addEventListener('click', handleClick)
    })

    return () => {
      clickables.forEach((clickable: Element) => {
        clickable.removeEventListener('click', handleClick)
      })
    }
  }, [messages])

  // const getDummyResponse = () => {
  //   console.log('git')
  //   const message = {
  //     event: 'ui',
  //     data: {
  //       html: `
  //       <div>
  //       <div class='hover:bg-gray-100 px-2 py-1 rounded-md text-sm font-medium' id='//a[@data-quid="start-your-order-delivery-cta"]'>
  //           Delivery
  //       </div>
  //       <div class='hover:bg-gray-100 px-2 py-1 rounded-md text-sm font-medium' id='//a[@data-quid="start-your-order-carryout-cta"]'>
  //           Carryout
  //       </div>
  //   </div>
  //       `
  //     }
  //   }

  //   setMessages(currentMessages => [
  //     ...currentMessages,
  //     {
  //       id: nanoid(),
  //       display:
  //         message.event === 'thought' ? (
  //           <BotThought>{message.data.thought}</BotThought>
  //         ) : message.event === 'ui' ? (
  //           <BotUI>
  //             <div
  //               ref={containerRef}
  //               dangerouslySetInnerHTML={{ __html: message.data.html }}
  //             />
  //             {/* {message.data.html} */}
  //           </BotUI>
  //         ) : null
  //     }
  //   ])
  // }

  if (socket) {
    // socket.onopen = function () {
    //   socket.send(JSON.stringify({ event: 'start' }))
    // }

    socket.onmessage = function (event) {
      console.log('Received message:', event.data)

      try {
        const message = JSON.parse(event.data)
        setMessages(currentMessages => [
          ...currentMessages,
          {
            id: nanoid(),
            display:
              message.event === 'thought' ? (
                <BotThought>{message.data.thought}</BotThought>
              ) : message.event === 'ui' ? (
                <BotUI>
                  <div
                    ref={containerRef}
                    dangerouslySetInnerHTML={{ __html: message.data.html }}
                  />
                </BotUI>
              ) : null
          }
        ])

        console.log('Parsed message:', message)
      } catch (e) {
        console.error('Error parsing message:', e)
      }
    }
  }

  return (
    <div className="fixed inset-x-0 bg-white/90 bottom-0 w-full duration-300 ease-in-out peer-[[data-state=open]]:group-[]:lg:pl-[250px] peer-[[data-state=open]]:group-[]:xl:pl-[300px] dark:from-10%">
      <SocketIndicator socket={socket} />

      <ButtonScrollToBottom
        isAtBottom={isAtBottom}
        scrollToBottom={scrollToBottom}
      />

      <div className="mx-auto sm:max-w-2xl sm:px-4">
        <div className="mb-4 grid sm:grid-cols-2 gap-2 sm:gap-4 px-4 sm:px-0">
          {messages.length === 0 &&
            exampleMessages.map((example, index) => (
              <div
                key={example.heading}
                className={cn(
                  'cursor-pointer bg-zinc-50 text-zinc-950 rounded-2xl p-4 sm:p-6 hover:bg-zinc-100 transition-colors',
                  index > 1 && 'hidden md:block'
                )}
                onClick={() => {
                  setMessages(currentMessages => [
                    ...currentMessages,
                    {
                      id: nanoid(),
                      display: <UserMessage>{example.message}</UserMessage>
                    }
                  ])

                  try {
                    submitUserMessage(example.message)
                  } catch {
                    toast(
                      <div className="text-red-600">
                        You have reached your message limit! Please try again
                        later, or{' '}
                        <a
                          className="underline"
                          target="_blank"
                          rel="noopener noreferrer"
                          href="https://vercel.com/templates/next.js/gemini-ai-chatbot"
                        >
                          deploy your own version
                        </a>
                        .
                      </div>
                    )
                  }
                }}
              >
                <div className="font-medium">{example.heading}</div>
                <div className="text-sm text-zinc-800">
                  {example.subheading}
                </div>
              </div>
            ))}
        </div>

        {messages?.length >= 2 ? (
          <div className="flex h-fit items-center justify-center">
            <div className="flex space-x-2">
              {id && title ? (
                <>
                  <Button
                    variant="outline"
                    onClick={() => setShareDialogOpen(true)}
                  >
                    <IconShare className="mr-2" />
                    Share
                  </Button>
                  <ChatShareDialog
                    open={shareDialogOpen}
                    onOpenChange={setShareDialogOpen}
                    onCopy={() => setShareDialogOpen(false)}
                    shareChat={shareChat}
                    chat={{
                      id,
                      title,
                      messages: aiState.messages
                    }}
                  />
                </>
              ) : null}
            </div>
          </div>
        ) : null}

        <div className="grid gap-4 sm:pb-4">
          <PromptForm input={input} setInput={setInput} />
          <FooterText className="hidden sm:block" />
        </div>
      </div>
    </div>
  )
}
